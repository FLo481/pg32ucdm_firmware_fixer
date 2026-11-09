# ASUS ROG Swift PG32UCDM: Auto KVM Detection fix

A small patch for firmware **MCM311** that makes the monitor's *Auto KVM Detection* work.

With stock firmware, the KVM stayed on its current USB upstream port when switching between a PC on USB-B and a laptop on USB-C, so the port had to be changed by hand in the menu. With this patch, the KVM follows the USB port assigned to the input on screen.

This repository contains only the patch script. You need the official firmware package from ASUS, more specifically firmware version MCM311.

> **Warning:** Flashing modified firmware is at your own risk and can leave the monitor unusable. It may also affect your warranty. This patch has only been tested on one monitor, with MCM311. This project is not affiliated with or endorsed by ASUS.

## Requirements

- ASUS PG32UCDM
- The **MCM311** OneKeyUpdate package from ASUS (`ASUSFirmwareOneKeyUpdate.exe`)
- Python 3 (no extra packages)
- A Windows PC to run the flashing tool

The `PG32UCDM.bin` from the USB flash drive update does not work with this script, and the patched image must not be installed with the USB drive method.

## Usage

1. Extract `ASUSFirmwareOneKeyUpdate.exe` with, for example, 7-Zip (it is a self-extracting archive) and keep a copy of the original EXE.

2. Build the patched image from the extracted firmware:

   ```
   python make_autokvm.py Scaler/ISPTool/ASUS_PG32UCDM_Project.bin patched.bin
   ```

3. Check the SHA-256 printed by the script:

   | File | SHA-256 |
   |---|---|
   | Original `ASUS_PG32UCDM_Project.bin` | `80e666e7441d6690dc45b4316f26b9bd8e593ea807fcbda012f82cf1b4b56aa2` |
   | `patched.bin` | `b0f4235d3d009662c657577ef09a978e4ddf00b6bce69290604fa5768c182328` |

4. Replace `Scaler/ISPTool/ASUS_PG32UCDM_Project.bin` with `patched.bin`, keeping the original filename.

5. Run `FirmwareOneKeyUpdate.exe` from the extracted folder (not the original `ASUSFirmwareOneKeyUpdate.exe`). Connect the monitor as described in ASUS's update instructions and do not disconnect it while flashing. Installing over stock MCM311 works.

6. On the monitor, open **USB Setup > KVM**, turn on **Auto KVM Detection**, and assign a port to each input. For a laptop on USB-C and a PC on USB-B:

   | Input | Port |
   |---|---|
   | USB-C | USB-C |
   | DisplayPort | USB-B |
   | HDMI-1 | USB-B |
   | HDMI-2 | USB-B |

7. If it does not switch at first, change the USB-C input's assignment from USB-B to USB-C by hand once.

## Going back to stock

Run the original `ASUSFirmwareOneKeyUpdate.exe` from ASUS.

## Limitations

- Only MCM311 is supported. The script stops if the expected bytes are not found, and other versions need the patch locations found again.
- An official ASUS firmware update replaces the patch.
- While Auto KVM Detection is on, the KVM follows the input, so a manual or hotkey switch will not stick.

## How it works

The firmware stores a USB port assignment for each input, but `KVM_AutoPoll` (`0x8610bfa0`) only used it when two status bytes, `0xa00088f0` and `0xa003f83c`, were `1` and `0`. Those bytes are not written by the main firmware code, and their exact meaning is unknown.

The patch changes two branch instructions. While Auto KVM Detection is on and an input has a stable picture, the firmware always looks up the assignment for the current input and applies it.

| Address | File offset | Original | Patched | Change |
|---|---|---|---|---|
| `0x8610bfe2` | `0x10BFE2` | `17 61` | `06 10` | `btnez 0x8610c012` to `b 0x8610bff0`: skip the status check |
| `0x8610c0ce` | `0x10C0CE` | `A1 17` | `D4 17` | `b 0x8610c012` to `b 0x8610c078`: apply the assignment directly |

The image's main code runs at `0x86000000`, so a file offset is the address minus that base. It uses MIPS16e-style code in which `jal` and `jr` appear to have no delay slots, so standard disassembler output can be misleading.

*Generated with AI, so check everything before trying this.*
