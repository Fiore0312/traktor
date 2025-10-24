#!/usr/bin/env python3
"""
MIDI Setup Verification Script
================================
Quick diagnostic tool to verify MIDI environment is ready

Checks:
- python-rtmidi installation
- IAC Driver availability
- MIDI port access
- Driver initialization
"""

import sys
from pathlib import Path
import platform

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def print_check(message, status, details=None):
    """Print formatted check result"""
    symbol = f"{GREEN}+{RESET}" if status else f"{RED}-{RESET}"
    print(f"{symbol} {message}")
    if details:
        print(f"  {details}")


def main():
    """Run all verification checks"""
    print("=" * 70)
    print("TRAKTOR MIDI DRIVER - SETUP VERIFICATION")
    print("=" * 70)
    print()

    all_passed = True

    # Check 1: MIDI backend availability (rtmidi or pygame)
    print("[1/5] Checking MIDI backend...")
    has_rtmidi = False
    has_pygame = False
    try:
        import rtmidi
        has_rtmidi = True
        print_check("python-rtmidi available", True)
    except ImportError:
        print_check("python-rtmidi available", False, "Using pygame fallback on Windows")

    if platform.system() == 'Windows':
        try:
            import pygame.midi
            pygame.midi.init()
            has_pygame = True
            print_check("pygame.midi available (Windows fallback)", True)
        except ImportError:
            print_check("pygame.midi available", False, "Install with: pip install pygame")
            all_passed = False
            return 1
        except pygame.error as e:
            print_check("pygame.midi init", False, str(e))
            all_passed = False
            return 1
    else:
        if not has_rtmidi:
            print_check("rtmidi required on non-Windows", False)
            all_passed = False
            return 1

    # Check 2: MIDI port availability
    print("\n[2/5] Checking MIDI ports...")
    ports = []
    if has_rtmidi:
        try:
            midi_out = rtmidi.MidiOut()
            ports = midi_out.get_ports()
            if ports:
                print_check(f"Found {len(ports)} MIDI port(s)", True)
                for idx, port in enumerate(ports):
                    print(f"    [{idx}] {port}")
            else:
                print_check("MIDI ports available", False, "No MIDI ports found")
                all_passed = False
        except Exception as e:
            print_check("MIDI ports accessible", False, str(e))
            all_passed = False
    else:
        try:
            count = pygame.midi.get_count()
            for i in range(count):
                info = pygame.midi.get_device_info(i)
                if info[3] == 1:  # output devices
                    name = info[1].decode('utf-8')
                    ports.append(name)
            if ports:
                print_check(f"Found {len(ports)} MIDI output port(s)", True)
                for idx, port in enumerate(ports):
                    print(f"    [{idx}] {port}")
            else:
                print_check("MIDI ports available", False, "No MIDI ports found")
                all_passed = False
        except Exception as e:
            print_check("pygame MIDI ports accessible", False, str(e))
            all_passed = False
    if not ports:
        all_passed = False

    # Check 3: IAC Driver Bus 1 presence
    if platform.system() == 'Windows':
        print("\n[3/5] Checking for Traktor MIDI Bus 1...")
        target_name = 'Traktor MIDI Bus 1'
        iac_found = False
        iac_port_name = None
        for port in ports:
            if target_name in port:
                iac_found = True
                iac_port_name = port
                break
        if iac_found:
            print_check(f"{target_name} found", True, iac_port_name)
        else:
            print_check(f"{target_name} found", False)
            print(f"\n{YELLOW}Setup Instructions for Windows:{RESET}")
            print("  1. Install loopMIDI from Tobias Erichsen (free virtual MIDI port)")
            print("  2. Create a new virtual port named 'Traktor MIDI Bus 1'")
            print("  3. Make sure it's enabled and running")
            print("  4. In Traktor, select this port in MIDI setup")
            all_passed = False
            return 1
    else:
        print("\n[3/5] Checking for IAC Driver Bus 1...")
        iac_found = False
        iac_port_name = None
        for port in ports:
            if "IAC" in port and "Bus 1" in port:
                iac_found = True
                iac_port_name = port
                break
        if iac_found:
            print_check("IAC Driver Bus 1 found", True, iac_port_name)
        else:
            print_check("IAC Driver Bus 1 found", False)
            print(f"\n{YELLOW}Setup Instructions:{RESET}")
            print("  1. Open Audio MIDI Setup (Cmd+Space → 'Audio MIDI Setup')")
            print("  2. Window menu → Show MIDI Studio")
            print("  3. Double-click 'IAC Driver' icon")
            print("  4. Check 'Device is online'")
            print("  5. Ensure 'Bus 1' exists in Ports list\n")
            all_passed = False
            return 1

    # Check 4: Driver files present
    print("\n[4/5] Checking driver files...")
    driver_path = Path(__file__).parent / "traktor_midi_driver.py"
    test_path = Path(__file__).parent / "test_load_track.py"

    files_ok = True
    if driver_path.exists():
        print_check("traktor_midi_driver.py exists", True)
    else:
        print_check("traktor_midi_driver.py exists", False)
        files_ok = False
        all_passed = False

    if test_path.exists():
        print_check("test_load_track.py exists", True)
    else:
        print_check("test_load_track.py exists", False, "Optional ad-hoc test file - can be recreated if needed")
        # Note: Test file is optional for production; core MIDI is verified
        files_ok = False  # Non-fatal for full setup

    # Check 5: Test driver initialization
    print("\n[5/5] Testing driver initialization...")
    try:
        # Import the driver
        sys.path.insert(0, str(Path(__file__).parent))
        from traktor_midi_driver import TraktorMIDIDriver

        # Try to initialize
        driver = TraktorMIDIDriver(port_name=iac_port_name)

        if driver.is_connected:
            print_check("Driver initialized successfully", True)

            # Test sending a harmless MIDI message (Master Volume set to current)
            print("\n  Testing MIDI communication...")
            test_result = driver.send_cc(cc_number=7, value=100, channel=0)

            if test_result:
                print_check("MIDI message sent successfully", True)
            else:
                print_check("MIDI message sent successfully", False)
                all_passed = False

            driver.close()
        else:
            print_check("Driver initialized successfully", False)
            all_passed = False

    except Exception as e:
        print_check("Driver initialization", False, str(e))
        all_passed = False
        return 1

    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print(f"{GREEN}+ ALL CHECKS PASSED - READY TO USE{RESET}")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Start Traktor Pro 3")
        print("  2. Configure MIDI mapping in Traktor (see MIDI_DRIVER_USAGE.md)")
        print("  3. Select a track in Traktor browser")
        print("  4. Run: python3 test_load_track.py")
        return 0
    else:
        print(f"{RED}X SOME CHECKS FAILED - SETUP INCOMPLETE{RESET}")
        print("=" * 70)
        print("\nReview the errors above and fix the issues.")
        print("See MIDI_DRIVER_USAGE.md for detailed setup instructions.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
