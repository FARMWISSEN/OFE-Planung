#!/usr/bin/env python3
"""
Compile Qt .ts translation files to .qm binary format.

This is a pure-Python replacement for Qt's lrelease tool,
useful when lrelease is not available in the environment.

Usage:
    python compile_translations.py [input.ts] [output.qm]
    python compile_translations.py              # compiles all .ts in i18n/

Reference: Qt source qttools/src/linguist/shared/qm.cpp
"""

import os
import struct
import sys
import xml.etree.ElementTree as ET

# QM file magic number (16 bytes)
QM_MAGIC = bytes([
    0x3C, 0xB8, 0x64, 0x18, 0xCA, 0xEF, 0x9C, 0x95,
    0xCD, 0x21, 0x1C, 0xBF, 0x60, 0xA1, 0xBD, 0xDD,
])

# Section tags (from QTranslatorPrivate in qtranslator.cpp)
TAG_CONTEXTS = 0x2F
TAG_HASHES = 0x42
TAG_MESSAGES = 0x69
TAG_NUMERUS_RULES = 0x88
TAG_DEPENDENCIES = 0x96
TAG_LANGUAGE = 0xA7

# Message sub-tags
MSG_END = 1
MSG_TRANSLATION = 3
MSG_SOURCE_TEXT = 6
MSG_CONTEXT = 7
MSG_COMMENT = 8


def elf_hash(data: bytes) -> int:
    """Qt's elfHash function used for translation lookups."""
    h = 0
    for byte in data:
        h = ((h << 4) + byte) & 0xFFFFFFFF
        g = h & 0xF0000000
        if g:
            h ^= g >> 24
        h &= ~g & 0xFFFFFFFF
    return h if h != 0 else 1


def make_message_entry(context: str, source: str, translation: str,
                       comment: str = '') -> bytes:
    """Build a single message entry for the Messages section.

    All sub-tag lengths are 4-byte big-endian (read32 in Qt source).
    The match() function in Qt strips a trailing null from data,
    so we include null terminators for context/source/comment.
    """
    parts = []

    # Translation (tag 3): 4-byte length + UTF-16BE data
    trans_bytes = translation.encode('utf-16-be')
    parts.append(struct.pack('B', MSG_TRANSLATION))
    parts.append(struct.pack('>I', len(trans_bytes)))
    parts.append(trans_bytes)

    # Context (tag 7): 4-byte length + UTF-8 null-terminated
    ctx_bytes = context.encode('utf-8') + b'\x00'
    parts.append(struct.pack('B', MSG_CONTEXT))
    parts.append(struct.pack('>I', len(ctx_bytes)))
    parts.append(ctx_bytes)

    # Source text (tag 6): 4-byte length + UTF-8 null-terminated
    src_bytes = source.encode('utf-8') + b'\x00'
    parts.append(struct.pack('B', MSG_SOURCE_TEXT))
    parts.append(struct.pack('>I', len(src_bytes)))
    parts.append(src_bytes)

    # Comment (tag 8): 4-byte length + UTF-8 null-terminated
    if comment:
        cmt_bytes = comment.encode('utf-8') + b'\x00'
        parts.append(struct.pack('B', MSG_COMMENT))
        parts.append(struct.pack('>I', len(cmt_bytes)))
        parts.append(cmt_bytes)

    # End marker (tag 1)
    parts.append(struct.pack('B', MSG_END))

    return b''.join(parts)


def compute_hash(source: str, comment: str = '') -> int:
    """Compute the lookup hash for a message."""
    key = source.encode('utf-8')
    if comment:
        key += comment.encode('utf-8')
    return elf_hash(key)


def parse_ts_file(ts_path: str):
    """Parse a .ts file and return list of (context, source, translation, comment)."""
    tree = ET.parse(ts_path)
    root = tree.getroot()
    messages = []

    for ctx_elem in root.findall('context'):
        ctx_name = ctx_elem.find('name').text or ''
        for msg_elem in ctx_elem.findall('message'):
            source_elem = msg_elem.find('source')
            trans_elem = msg_elem.find('translation')
            comment_elem = msg_elem.find('comment')

            source = source_elem.text if source_elem is not None and source_elem.text else ''
            translation = trans_elem.text if trans_elem is not None and trans_elem.text else ''
            comment = comment_elem.text if comment_elem is not None and comment_elem.text else ''

            # Skip entries with 'type="unfinished"' or empty translations
            if trans_elem is not None and trans_elem.get('type') == 'unfinished':
                continue
            if not translation:
                continue

            messages.append((ctx_name, source, translation, comment))

    return messages


def compile_qm(messages, language: str = '') -> bytes:
    """Compile a list of messages into QM binary format."""
    # Build Messages section
    msg_entries = []
    offsets = []
    current_offset = 0

    for ctx, src, trans, comment in messages:
        entry = make_message_entry(ctx, src, trans, comment)
        offsets.append(current_offset)
        msg_entries.append(entry)
        current_offset += len(entry)

    messages_data = b''.join(msg_entries)

    # Build Hashes section (sorted by hash value)
    hash_entries = []
    for i, (ctx, src, trans, comment) in enumerate(messages):
        h = compute_hash(src, comment)
        hash_entries.append((h, offsets[i]))

    hash_entries.sort(key=lambda x: x[0])
    hashes_data = b''.join(
        struct.pack('>II', h, offset) for h, offset in hash_entries
    )

    # Build the file
    output = bytearray()
    output.extend(QM_MAGIC)

    # Hashes section
    output.append(TAG_HASHES)
    output.extend(struct.pack('>I', len(hashes_data)))
    output.extend(hashes_data)

    # Messages section
    output.append(TAG_MESSAGES)
    output.extend(struct.pack('>I', len(messages_data)))
    output.extend(messages_data)

    # Language section (if specified)
    if language:
        lang_data = language.encode('utf-8')
        output.append(TAG_LANGUAGE)
        output.extend(struct.pack('>I', len(lang_data)))
        output.extend(lang_data)

    return bytes(output)


def compile_ts_to_qm(ts_path: str, qm_path: str = None):
    """Compile a .ts file to .qm format."""
    if qm_path is None:
        qm_path = os.path.splitext(ts_path)[0] + '.qm'

    messages = parse_ts_file(ts_path)
    if not messages:
        print(f"Warning: No translations found in {ts_path}")
        return

    # Extract language from TS file
    tree = ET.parse(ts_path)
    root = tree.getroot()
    language = root.get('language', '')

    qm_data = compile_qm(messages, language)

    with open(qm_path, 'wb') as f:
        f.write(qm_data)

    print(f"Compiled {len(messages)} messages: {ts_path} -> {qm_path}")


def main():
    if len(sys.argv) >= 2:
        ts_path = sys.argv[1]
        qm_path = sys.argv[2] if len(sys.argv) >= 3 else None
        compile_ts_to_qm(ts_path, qm_path)
    else:
        # Compile all .ts files in i18n/ directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        i18n_dir = os.path.join(os.path.dirname(script_dir), 'i18n')

        if not os.path.isdir(i18n_dir):
            print(f"Error: i18n directory not found at {i18n_dir}")
            sys.exit(1)

        count = 0
        for filename in os.listdir(i18n_dir):
            if filename.endswith('.ts'):
                ts_path = os.path.join(i18n_dir, filename)
                compile_ts_to_qm(ts_path)
                count += 1

        if count == 0:
            print("No .ts files found in i18n/")
        else:
            print(f"\nDone: compiled {count} file(s)")


if __name__ == '__main__':
    main()
