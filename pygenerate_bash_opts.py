#!/usr/bin/env python3
"""Shell option and help generator"""
__author__ = "PsykoCat"
__maintainer__ = __author__
__email__ = __author__ + "at nomail dot localhost"
__license__ = "Apache License 2.0"
__version__ = "0.0.1"

import argparse
import logging
import os
import subprocess
import sys
try:
    import csv
    import json
    import yaml
except ImportError as e:
    logging.error("Please download the following python libs : csv, json, yaml")
    sys.exit(1)

__VERSION__ = "0.0.1"

################################################################################
# Internal definitions
################################################################################

################################################################################
# Public definitions
################################################################################
def parse_as_csv(csvstream):
    """Parse input as csv stream"""
    _csv_output = []
    csv.Sniffer().sniff(csvstream.read(1024))
    csvstream.seek(0)
    for _row in csv.reader(filter(lambda row: row[0]!="#", csvstream),
                           delimiter=";", quotechar='"'):
        _csv_output.append({
            "options": _row[0],
            "destination": _row[1],
            "has_argument": _row[2],
            "help_text": _row[3],
        })
    return ({}, _csv_output)

def parse_as_json(jsonstream):
    """Parse input as json stream"""
    _json_output = json.load(jsonstream)
    return (_json_output["generator_opts"], _json_output["bash_opts"])

def parse_as_yaml(yamlstream):
    """Parse input as yaml stream"""
    _yaml_output = yaml.load(yamlstream, Loader=yaml.SafeLoader)
    return (_yaml_output["generator_opts"], _yaml_output["bash_opts"])

def parse_opts_output(opt_file):
    """Parse opts files"""
    _output = []

    _base_err_msg = "%sopt_file is not a %s."
    _format_err_msg = "%s file found, but the format is incorrect."
    _unhandled_prefix_msg = "[UNHANDLED] "
    with open(opt_file, "r") as _stream:
        __current_type = "YAML"
        try:
            _output = parse_as_yaml(_stream)
            return _output
        except TypeError as e:
            logging.debug(_base_err_msg, "", __current_type)
        except yaml.scanner.ScannerError as e:
            logging.error(_format_err_msg, __current_type)
            print("%s%s" % (e.problem, e.problem_mark))
            sys.exit(1)
        except yaml.parser.ParserError as e:
            logging.error(_format_err_msg, __current_type)
            print("%s%s" % (e.problem, e.problem_mark))
            sys.exit(1)
        # Keep this one in case we forgot exceptions to handle
        except:
            logging.error(_base_err_msg, _unhandled_prefix_msg, __current_type)
            raise

        # Rewind for the other test
        _stream.seek(0)

        __current_type = "JSON"
        try:
            _output = parse_as_json(_stream)
            return _output
        except json.decoder.JSONDecodeError as e:
            logging.debug(_base_err_msg, "", __current_type)
        # Keep this one in case we forgot exceptions to handle
        except:
            logging.error(_base_err_msg, _unhandled_prefix_msg, __current_type)
            raise

        # Rewind for the other test
        _stream.seek(0)

        __current_type = "CSV"
        try:
            _output = parse_as_csv(_stream)
            return _output
        except csv.Error as e:
            logging.debug(_base_err_msg, "", __current_type)
        except IndexError as e:
            logging.debug(_base_err_msg, "", __current_type)
        # Keep this one in case we forgot exceptions to handle
        except:
            logging.error(_base_err_msg, _unhandled_prefix_msg, __current_type)
            raise


def process_bash_infos(opt_infos, usage=None, description=None, use_getopt=False,
                       true_false_choice=[], remains_as_args=False,
                       add_debug=False, add_test=False):
    """Generator"""
    __indent="\t"
    if true_false_choice == []:
        true_false_choice=["yes", ""]
    _parser = []
    _parser_header = []
    _parser_usage = []
    _parser_beg = []
    _parser_opts = []
    _parser_end = []
    _parser_footer = []
    if usage:
        usage = "%(prog)s " + usage
    _bash_help = argparse.ArgumentParser(prog="${0}", usage=usage,
                                         description=description)

    for _opt in opt_infos:
        __arglist = []
        __argdict = {}
        __bashparse = ""
        __tmp = []

        ## First argument : the option(s)
        if _opt.get("options", ""):
            for __subopt in _opt["options"].split(","):
                if len(__subopt) == 1:
                    __tmp.append("-"+__subopt)
                else:
                    __tmp.append("--"+__subopt)
                __arglist.append(__tmp[-1])
            __argdict.update({"dest": _opt["destination"]})
        elif _opt.get("elements", ""):
            for __subopt in _opt["elements"].split(","):
                __tmp.append(__subopt)
            __arglist.append(_opt["destination"])
            __argdict.update({"choices": __tmp})

        __bashparse = "|".join(__tmp)+") "
        ## Second argument : the destination
        _parser_beg.append(_opt["destination"]+'="'+true_false_choice[1]+'"')

        ## Third argument : the argument
        ## (only for options as elements are automatically 'self')
        if _opt.get("options", ""):
            logging.info(_opt["has_argument"])
            if _opt["has_argument"] == "self":
                __argdict.update({"action":"store_true"})
                __bashparse += _opt["destination"] + '="${1#--}";;'
            elif _opt["has_argument"] == "yes" or _opt["has_argument"] == True:
                __argdict.update({"action":"store"})
                __bashparse += "shift; "+ _opt["destination"] + '="${1}";;'
            else:
                __argdict.update({"action":"store_true"})
                __bashparse += _opt["destination"] + '="' + \
                               true_false_choice[0]+'";;'
        elif _opt.get("elements", ""):
            __bashparse += _opt["destination"] + '="${1}";;'

        ## Fourth argument: the help
        __argdict.update({"help": _opt["help_text"]})

        logging.debug("arglist : %s",__arglist)
        logging.debug("argdict : %s", __argdict)
        logging.debug("bashparse : %s",__bashparse)
        logging.debug("")

        if add_test:
            _parser_footer.append('echo "' + _opt["destination"] + \
                                  '=${' + _opt["destination"] + '}"')

        _bash_help.add_argument(*__arglist, **__argdict)
        _parser_opts.append(__indent + __indent + __bashparse)

    _parser_header.append("#!/usr/bin/env bash")
    _parser_header.append("set -eu")
    _parser_header.append("")

    ## Parse remains arguments
    if remains_as_args:
        _parser_beg.append("declare -a args=()")
        _parser_opts.append(__indent+__indent+'*) args+=("${1}");;')
        if add_test:
            _parser_footer.append('echo "args=${args[@]}"')
    else:
        _parser_opts.append(__indent+__indent+'*) ;;')

    # Usage parsing
    _parser_usage.append("function usage(){")
    _parser_usage.append(__indent + "cat > /dev/stderr <<-EOF")
    for __line in _bash_help.format_help().splitlines():
        __begin = ""
        if __line:
            __begin = __indent
        _parser_usage.append(__begin + __line.rstrip())
    _parser_usage.append(__indent + "EOF")
    _parser_usage.append("}")
    _parser_usage.append("")

    # Pre parsing
    _parser_beg.append("")
    _parser_beg.append("while [ $# -ne 0 ]; do")
    _parser_beg.append(__indent+'case "${1,,}" in')
    _parser_beg.append(__indent+__indent+"--) shift; break;;")
    _parser_beg.append(__indent+__indent+"-h|-help|--help) usage; exit 1;;")
    if add_debug:
        _parser_beg.append(__indent+__indent+"--debug) set -x;;")
    # Options parsing

    # Post parsing
    _parser_end.append(__indent+"esac")
    _parser_end.append(__indent+"shift;")
    _parser_end.append("done")
    _parser_end.append("")

    if add_test:
        _parser_footer.append("")

    _parser_footer.append("#END\n")
    # Combine everything
    _parser.extend(_parser_header)
    _parser.extend(_parser_usage)
    _parser.extend(_parser_beg)
    _parser.extend(_parser_opts)
    _parser.extend(_parser_end)
    _parser.extend(_parser_footer)

    return _parser

################################################################################
# Main related functions
################################################################################
def _parse_args(**kwargs):
    """Global parser, will provide common options
    but the parse_args is to be made by the caller"""
    parser = argparse.ArgumentParser(**kwargs)
    base_opts = parser.add_argument_group("Base options")
    base_opts.add_argument("-v", "--verbose", dest="verbosity",
                           action="store_const", default=logging.INFO,
                           const=logging.DEBUG, help="Be verbose")
    base_opts.add_argument("-q", "--quiet", dest="verbosity",
                           action="store_const", const=logging.ERROR,
                           help="Be quiet")
    base_opts.add_argument("--version", action="version",
                           version="%(prog)s " + __version__)
    base_opts.add_argument("--no-color", dest="log_color", action="store_false",
                           help="Disable colorful logs")
    base_opts.add_argument("--color", dest="log_color", action="store_true",
                           help="Have colorful logs")
    base_opts.add_argument("-n", "--dry-run", dest="dryrun",
                           action="store_true", help="Dry run")
    return parser

def _setup_log(opts):
    """Basic log setup config, with color customization"""
    verbosity = opts.verbosity
    has_color = opts.log_color

    # Color definitions
    clr_default = "\033[m"
    clr_red = "\033[31m"
    clr_green = "\033[32m"
    clr_yellow = "\033[33m"

    # Define log level decoration for messages
    if not has_color:
        clr_red = clr_yellow = clr_green = clr_default = ""

    # Associate log level with decoration
    level_colors_d = {
        logging.CRITICAL: clr_red + "[C] ",
        logging.ERROR: clr_red + "[E] ",
        logging.WARNING: clr_yellow + "[W] ",
        logging.INFO: clr_green + "[I] ",
        logging.DEBUG: clr_default + "",
    }

    if verbosity is None:
        verbosity = logging.INFO

    # Assigning colors to levels
    fmt = "%(levelname)s%(message)s" + clr_default
    # For each log level specified, set its corresponding visual
    for (log_level, log_deco) in level_colors_d.items():
        logging.addLevelName(log_level, log_deco)
    # Configure logging system
    logging.basicConfig(format=fmt, level=verbosity, stream=sys.stderr)

def parse_args(args=None, **kwargs):
    """Main parse_args caller with specific options"""
    parser = _parse_args(**kwargs)
    parser.add_argument("optfiles", nargs="+", help="Option files to parse")
    parser.add_argument("-g", "--getopt", action="store_true",
                        help="Use getopt as a parser.")
    parser.add_argument("-o", "--output", dest="output_file",
                        default="/dev/stdout", help="Where to generate output")
    parser.add_argument("-a", "--remains-as-args", action="store_true",
                        help="Store remaining args (default is discarding)")
    parser.add_argument("-d", "--add-debug", action="store_true",
                        help="Add debugging in script")
    parser.add_argument("--add-test", action="store_true",
                        help="Add a testing print part.")
    return (parser, parser.parse_args(args))

def main(args=None):
    """Main part"""
    (_parser, opts) = parse_args(args)
    _setup_log(opts)
    _default_opts = {
        "usage": None,
        "use_getopt": False,
        "output_file": "/dev/stdout",
        "true_false_choice": [],
        "remains_as_args": False,
        "add_debug": False,
        "add_test": False
    }
    _arguments_opts = {
        "output_file": opts.output_file,
        "use_getopt": opts.getopt,
        "remains_as_args": opts.remains_as_args,
        "add_debug": opts.add_debug,
        "add_test": opts.add_test
    }
    logging.debug("Default opts")
    logging.debug(_default_opts)
    logging.debug("")
    logging.debug("Arguments given opts")
    logging.debug(_arguments_opts)
    logging.debug("")
    _process_method_arguments = {}

    for __ofile in opts.optfiles:
        (_override_opts, _infos) = parse_opts_output(__ofile)
        logging.debug("Overriden opts")
        logging.debug(_override_opts)
        logging.debug("")
        # Check whether to use options in file
        if _default_opts == _override_opts or _override_opts == {}:
            _process_method_arguments = _arguments_opts
        else:
            _process_method_arguments = _override_opts
        logging.debug("Options given :")
        logging.debug(_process_method_arguments)
        logging.debug("")

        # Extract the output file as it serves after the processing
        __output_file = _process_method_arguments.pop("output_file")
        _output = process_bash_infos(_infos, **_process_method_arguments)

        with open(__output_file, "w") as _outfile:
            _outfile.write("\n".join(_output))

if __name__.__eq__("__main__"):
    main()

#END
