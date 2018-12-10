"""viol sphinx extensions"""

import optparse
import sys
from docutils import nodes
from docutils.parsers import rst
from docutils.statemachine import ViewList
from textwrap import dedent
from viol import commands
from viol import cmdoptions
from viol.utils.cli_opt_files import default_log_file
from viol.utils.util import get_prog


class ViolCommandUsage(rst.Directive):
    required_arguments = 1

    def run(self):
        cmd = commands[self.arguments[0]]
        prog = '%s %s' % (get_prog(), cmd.name)
        usage = dedent(cmd.usage.replace('%prog', prog))
        node = nodes.literal_block(usage, usage)
        return [node]


class ViolCommandDescription(rst.Directive):
    required_arguments = 1

    def run(self):
        node = nodes.paragraph()
        node.document = self.state.document
        desc = ViewList()
        description = dedent(commands[self.arguments[0]].__doc__)
        for line in description.split('\n'):
            desc.append(line, "")
        self.state.nested_parse(desc, 0, node)
        return [node]


class ViolOptions(rst.Directive):

    def _format_option(self, option, cmd_name=None):
        if cmd_name:
            bookmark_line = ".. _`%s_%s`:" % (cmd_name, option._long_opts[0])
        else:
            bookmark_line = ".. _`%s`:" % option._long_opts[0]
        line = ".. option:: "
        if option._short_opts:
            line += option._short_opts[0]
        if option._short_opts and option._long_opts:
            line += ", %s" % option._long_opts[0]
        elif option._long_opts:
            line += option._long_opts[0]
        if option.takes_value():
            metavar = option.metavar or option.dest.lower()
            line += " <%s>" % metavar.lower()
        # fix defaults
        opt_help = option.help.replace('%default', str(option.default))
        # fix paths with sys.prefix
        opt_help = opt_help.replace(sys.prefix, "<sys.prefix>")
        opt_help = opt_help.replace(
            default_log_file,
            "<see :ref:`FileLogging`>",
        )
        return [bookmark_line, "", line, "", "    %s" % opt_help, ""]

    def _format_options(self, options, cmd_name=None):
        for option in options:
            if option.help == optparse.SUPPRESS_HELP:
                continue
            for line in self._format_option(option, cmd_name):
                self.view_list.append(line, "")

    def run(self):
        node = nodes.paragraph()
        node.document = self.state.document
        self.view_list = ViewList()
        self.process_options()
        self.state.nested_parse(self.view_list, 0, node)
        return [node]


class ViolGeneralOptions(ViolOptions):
    def process_options(self):
        self._format_options(
            [o.make() for o in cmdoptions.general_group['options']]
        )


class ViolFileLocaleOptions(ViolOptions):
    def process_options(self):
        self._format_options(
            [o.make() for o in cmdoptions.file_locale_group['options']]
        )


class ViolFileOutputOptions(ViolOptions):
    def process_options(self):
        self._format_options(
            [o.make() for o in cmdoptions.file_output_group['options']]
        )


class ViolCommandOptions(ViolOptions):
    required_arguments = 1

    def process_options(self):
        cmd = commands[self.arguments[0]]()
        self._format_options(
            cmd.parser.option_groups[0].option_list,
            cmd_name=cmd.name,
        )


def setup(app):
    app.add_directive('viol-command-usage', ViolCommandUsage)
    app.add_directive('viol-command-description', ViolCommandDescription)
    app.add_directive('viol-command-options', ViolCommandOptions)
    app.add_directive('viol-general-options', ViolGeneralOptions)
    app.add_directive('viol-file-locale-options', ViolFileLocaleOptions)
    app.add_directive('viol-file-output-options', ViolFileOutputOptions)