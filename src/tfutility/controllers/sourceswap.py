# -*- coding: utf-8 -*-
import enum
import re
import sys

from tfutility.core.base import Command
from tfutility.core.tffile import TfFile
from tfutility.core.tfpaths import TFPaths


class SWITCH_DIRECTION(enum.Enum):
    TO_LOCAL = 1
    TO_REMOTE = 2


class SourceSwapHandler(TFPaths, Command):
    name = "sourceswap"
    help = "Allows to switch module Sources. Between a Local and Remote Path"

    def add_arguments(self, parser):
        parser = super().add_arguments(parser)
        parser.add_argument(
            "-s",
            "--switch-to",
            type=str,
            choices=["l", "r", "local", "remote"],
            help="Define to which reference all decorated modules should be swapped",
        )
        return parser

    def block_switch_to(self, options, block, dec, switch_to):
        file_path = block.get_tf_file().path
        if not block.id.startswith("module"):
            self.get_logger().error(
                f"The decorator @sourceswap applied to wrong blocktype in {file_path}:{block.start}"
            )
            sys.exit(1)

        lines = block.get_tf_file().lines
        source_line = -1
        version_line = -1
        source_indent = ""
        for li in range(block.start, block.end):
            cline = lines[li]

            tf_key = re.match(r"(\s*)(\S*)\s*\=\s*.*", cline)
            if tf_key is None:
                continue

            if tf_key.group(2) == "source":
                source_line = li
                source_indent = tf_key.group(1)
            elif tf_key.group(2) == "version":
                version_line = li

        if switch_to is SWITCH_DIRECTION.TO_REMOTE:
            remote_source = dec.get_parameter("remote_source")
            remote_version = dec.get_parameter("remote_version")

            block.get_tf_file().lines[source_line] = re.sub(
                r"source\s*\=\s*\"(.*)\"",
                f'source = "{remote_source}"',
                block.get_tf_file().lines[source_line],
            )

            if version_line == -1:
                block.get_tf_file().lines.insert(
                    source_line, f'{source_indent}version = "{remote_version}"'
                )
            else:
                block.get_tf_file().lines[source_line] = re.sub(
                    r"version\s*\=\s*\"(.*)\"",
                    f'version = "{remote_version}"',
                    block.get_tf_file().lines[source_line],
                )

        else:
            local_source = dec.get_parameter("local_source")
            block.get_tf_file().lines[source_line] = re.sub(
                r"source\s*\=\s*\"(.*)\"",
                f'source = "{local_source}"',
                block.get_tf_file().lines[source_line],
            )

            if version_line > 0:
                del block.get_tf_file().lines[version_line]

    def get_decorator(self, block):
        file_path = block.get_tf_file().path
        dec = block.get_decorator(self.get_name())
        general_error = False
        for param_key in ["remote_source", "remote_version", "local_source"]:
            if not dec.get_parameter(param_key):
                self.get_logger().error(
                    f"Decorator {self.get_name()} {file_path}:{block.start} requires the parameters remote_source, remote_version, local_source"
                )
                general_error = True

        if general_error:
            sys.exit(1)
        return dec

    def handle(self, options):
        if not options.switch_to:
            self.get_logger().error(
                "Please use --switch-to argument with the keywords local or remote"
            )
            sys.exit(1)

        switch_to = SWITCH_DIRECTION.TO_REMOTE
        if options.switch_to in ["local", "l"]:
            switch_to = SWITCH_DIRECTION.TO_LOCAL

        tf_files = self.get_file_list(options.paths)

        for file in tf_files:
            file = TfFile(file)

            for block in file.get_blocks_with_decorator(self.get_name()):
                dec = self.get_decorator(block)
                self.block_switch_to(options, block, dec, switch_to)
            file.write_back()
