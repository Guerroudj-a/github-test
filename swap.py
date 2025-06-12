import os
import sys
import re

def find_swap_device():
    try:
        with open("/proc/swaps", "r") as f:
            lines = f.readlines()[1:]  # Skip header
            if not lines:
                print("No swap devices found.")
                return None
            for line in lines:
                parts = line.split()
                if parts and os.path.exists(parts[0]):
                    return parts[0]
        return None
    except Exception as e:
        print(f"Error reading /proc/swaps: {e}")
        return None

def is_printable_ascii(byte_seq):
    try:
        text = byte_seq.decode('ascii')
        return all(32 <= ord(c) <= 126 for c in text)
    except UnicodeDecodeError:
        return False

def read_swap_ascii_lines(path, line_count=10, line_len=10):
    try:
        with open(path, "rb") as f:
            chunk_size = 4096
            buffer = b""
            lines = []

            while len(lines) < line_count:
                data = f.read(chunk_size)
                if not data:
                    break
                buffer += data

                for i in range(0, len(buffer) - line_len + 1):
                    segment = buffer[i:i + line_len]
                    if is_printable_ascii(segment):
                        lines.append(segment.decode("ascii"))
                        if len(lines) >= line_count:
                            break

                buffer = buffer[-line_len:]  # keep last few bytes for next scan

            return lines
    except PermissionError:
        print(f"Permission denied while accessing {path}. Try running as root.")
        return []
    except Exception as e:
        print(f"Error reading swap file: {e}")
        return []

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Read printable ASCII strings from swap space.")
    parser.add_argument("lines", type=int, help="Number of lines to read")
    parser.add_argument("--length", type=int, default=10, help="Length of each line (default: 10)")
    args = parser.parse_args()

    swap_path = find_swap_device()
    if not swap_path:
        print("No readable swap device found.")
        return

    print(f"Reading from swap: {swap_path}")
    ascii_lines = read_swap_ascii_lines(swap_path, args.lines, args.length)

    if not ascii_lines:
        print("No readable ASCII content found.")
    else:
        for i, line in enumerate(ascii_lines, 1):
            print(f"[{i}] {line}")

if __name__ == "__main__":
    main()
