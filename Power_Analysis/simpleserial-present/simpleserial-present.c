#include "hal.h"
#include "simpleserial.h"
#include "present.h"

#include <stdint.h>
#include <string.h>

static uint8_t key[10] = {0};

uint8_t set_key(uint8_t *k, uint8_t len)
{
    if(len != 10)
        return 1;

    memcpy(key, k, 10);

    return 0;
}

uint8_t encrypt(uint8_t *pt,
                uint8_t len)
{
    if(len != 8)
        return 1;

    uint8_t buf[8];

    memcpy(buf, pt, 8);

    trigger_high();

    present80_encrypt(buf, key);

    trigger_low();

    simpleserial_put('r', 8, buf);

    return 0;
}

int main(void)
{
    platform_init();

    init_uart();

    trigger_setup();

    simpleserial_init();

    simpleserial_addcmd('k', 10, set_key);

    simpleserial_addcmd('p', 8, encrypt);

    while(1)
    {
        simpleserial_get();
    }
}
