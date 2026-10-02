import usb.core
import usb.util
import time

print("WATCHING USB STATE...", flush=True)

last = None

while True:
    d3 = usb.core.find(idVendor=0x0e8d, idProduct=0x0003)
    d2 = usb.core.find(idVendor=0x0e8d, idProduct=0x2000)

    state = "0003" if d3 else ("2000" if d2 else "NONE")

    if state != last:
        print(
            time.strftime("%H:%M:%S"),
            "STATE =", state,
            flush=True
        )
        last = state

    if d3:
        d = d3

        print("FOUND 0003 - IMMEDIATE TEST", flush=True)

        try:
            cfg = d[0]

            itf = usb.util.find_descriptor(
                cfg,
                bInterfaceNumber=1
            )

            ep_out = usb.util.find_descriptor(
                itf,
                custom_match=lambda e:
                    usb.util.endpoint_direction(e.bEndpointAddress)
                    == usb.util.ENDPOINT_OUT
            )

            ep_in = usb.util.find_descriptor(
                itf,
                custom_match=lambda e:
                    usb.util.endpoint_direction(e.bEndpointAddress)
                    == usb.util.ENDPOINT_IN
            )

            maxinsize = ep_in.wMaxPacketSize

            print("OUT =", hex(ep_out.bEndpointAddress), flush=True)
            print("IN  =", hex(ep_in.bEndpointAddress), flush=True)
            print("MAX =", maxinsize, flush=True)

            for b in b"\xa0\x0a\x50\x05":
                print("WRITE", hex(b), flush=True)

                w = ep_out.write(bytes([b]))

                print("WROTE", w, flush=True)

                v = bytes(ep_in.read(maxinsize))

                print(
                    "READ",
                    v.hex(),
                    "EXPECTED",
                    f"{(~b) & 0xff:02x}",
                    flush=True
                )

                if len(v) != 1 or v[0] != ((~b) & 0xff):
                    print("HANDSHAKE FAILED", flush=True)
                    break
            else:
                print("HANDSHAKE SUCCESS", flush=True)

        except Exception as e:
            print(
                "USB ERROR:",
                type(e).__name__,
                repr(e),
                flush=True
            )

        print("STOP", flush=True)
        break

    time.sleep(0.005)