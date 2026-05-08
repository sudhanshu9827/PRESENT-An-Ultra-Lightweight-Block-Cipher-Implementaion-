#include "present.h"

#include <stdint.h>
#include <string.h>

typedef struct __attribute__((__packed__)) {
    uint8_t nibble1 : 4;
    uint8_t nibble2 : 4;
} byte;

static const uint8_t S[] = {
    0xC,0x5,0x6,0xB,
    0x9,0x0,0xA,0xD,
    0x3,0xE,0xF,0x8,
    0x4,0x7,0x1,0x2
};

static const uint8_t P[] = {
     0,16,32,48,1,17,33,49,
     2,18,34,50,3,19,35,51,
     4,20,36,52,5,21,37,53,
     6,22,38,54,7,23,39,55,
     8,24,40,56,9,25,41,57,
    10,26,42,58,11,27,43,59,
    12,28,44,60,13,29,45,61,
    14,30,46,62,15,31,47,63
};

static uint64_t fromBytesToLong(byte* bytes)
{
    uint64_t result = 0;

    for(int i=0; i<8; i++) {

        result =
            (result << 4) |
            (bytes[i].nibble1 & 0xF);

        result =
            (result << 4) |
            (bytes[i].nibble2 & 0xF);
    }

    return result;
}

static void fromLongToBytes(uint64_t block,
                            byte* bytes)
{
    for(int i=7; i>=0; i--) {

        bytes[i].nibble2 =
            (block >> (2 * (7 - i) * 4)) & 0xF;

        bytes[i].nibble1 =
            (block >> ((2 * (7 - i) + 1) * 4)) & 0xF;
    }
}

static uint64_t permute(uint64_t source)
{
    uint64_t permutation = 0;

    for(int i=0; i<64; i++) {

        int distance = 63 - i;

        permutation |=
            ((source >> distance) & 0x1ULL)
            << (63 - P[i]);
    }

    return permutation;
}

static void generateSubkeys(uint8_t *masterKey,
                            uint64_t *subKeys)
{
    uint64_t keyHigh = 0;
    uint16_t keyLow = 0;

    for(int i=0; i<8; i++) {
        keyHigh =
            (keyHigh << 8) |
            masterKey[i];
    }

    keyLow =
        ((uint16_t)masterKey[8] << 8) |
        masterKey[9];

    subKeys[0] = keyHigh;

    for(int i=1; i<32; i++) {

        uint64_t temp1 = keyHigh;
        uint16_t temp2 = keyLow;

        keyHigh =
            (temp1 << 61) |
            ((uint64_t)temp2 << 45) |
            (temp1 >> 19);

        keyLow =
            (temp1 >> 3) & 0xFFFF;

        uint8_t temp =
            S[keyHigh >> 60];

        keyHigh &=
            0x0FFFFFFFFFFFFFFFULL;

        keyHigh |=
            ((uint64_t)temp << 60);

        keyLow ^=
            ((i & 0x01) << 15);

        keyHigh ^=
            (i >> 1);

        subKeys[i] = keyHigh;
    }
}

void present80_encrypt(uint8_t *block,
                       uint8_t *masterKey)
{
    uint64_t subkeys[32];

    generateSubkeys(masterKey,
                    subkeys);

    uint64_t state = 0;

    for(int i=0; i<8; i++) {
        state =
            (state << 8) |
            block[i];
    }

    byte stateBytes[8];

    for(int i=0; i<31; i++) {

        state ^= subkeys[i];

        fromLongToBytes(state,
                        stateBytes);

        for(int j=0; j<8; j++) {

            stateBytes[j].nibble1 =
                S[stateBytes[j].nibble1];

            stateBytes[j].nibble2 =
                S[stateBytes[j].nibble2];
        }

        state =
            permute(
                fromBytesToLong(stateBytes)
            );
    }

    state ^= subkeys[31];

    for(int i=7; i>=0; i--) {

        block[i] = state & 0xFF;

        state >>= 8;
    }
}
