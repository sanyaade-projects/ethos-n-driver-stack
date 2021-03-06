#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2018-2020 Arm Limited. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import SCons.Script
import SCons.Variables.PathVariable as PathVariable


def create_variables():
    '''
    Create a default scons var setup.

    This adds default parameters to the environment such as the options.py file,
    PATH and LD_LIBRARY_PATH are used for setting the respective environment variables,
    CPATH and LPATH are used for setting additional paths for C include files and library files respectively.

    Returns:
        (SCons.Script.Variables): The scons Variables pre-setup with common parameters
    '''
    options_var = SCons.Script.Variables()
    options_var.Add('options', 'Options for Sconstruct e.g. debug=0', 'options.py')
    env = SCons.Script.Environment(variables=options_var)
    # Create another Variables so we can have options appear in the help command
    var = SCons.Script.Variables(['dev_options.py', env['options']])
    var.AddVariables(
        ('options', 'Options for Sconstruct e.g. debug=0', 'options.py'),
        ('PATH', 'Prepend to the PATH environment variable'),
        ('LD_LIBRARY_PATH', 'Prepend to the LD_LIBRARY_PATH environment variable'),
        ('CPATH', 'Append to the C include path list the compiler uses'),
        ('LPATH', 'Append to the library path list the compiler uses'),

        ('scons_extra', 'Extra scons files to be loaded, separated by comma.', None),

        PathVariable('install_prefix', 'Installation prefix', os.path.join(os.path.sep, 'usr', 'local'),
                     PathVariable.PathAccept),
        PathVariable('install_bin_dir', 'Executables installation directory', os.path.join('$install_prefix', 'bin'),
                     PathVariable.PathAccept),
        PathVariable('install_include_dir', 'Header files installation directory',
                     os.path.join('$install_prefix', 'include'), PathVariable.PathAccept),
        PathVariable('install_lib_dir', 'Libraries installation directory', os.path.join('$install_prefix', 'lib'),
                     PathVariable.PathAccept),
    )
    return var


def load_extras(env, **params):
    "Load any extra scons scripts, specified in scons_extra variable"
    scriptpath = env.get('scons_extra')
    if scriptpath:
        print('Loading extra SConscripts: {}, with {}'.format(scriptpath, params))
        env.SConscript(scriptpath, exports=['env', 'params'])


def add_env_var(env, variable):
    '''
    Add a scons variable into the scons environment as an environment variable, but only if it has been set.

    Args:
        env (SCons.Environment): The scons environment to use
        variable          (str): The scons parameter to promote to an envvar
    '''
    if variable in env:
        env['ENV'][variable] = env[variable]


def parse_default_vars(env):
    '''
    Parse the default variables that are defined in the create_variables() function.

    Args:
        env (SCons.Environment): The scons environment to use
    '''
    # Import the ARMLMD_LICENSE_FILE environment variable into scons.
    if 'ARMLMD_LICENSE_FILE' in os.environ:
        env['ENV']['ARMLMD_LICENSE_FILE'] = os.environ['ARMLMD_LICENSE_FILE']
    # Allows colours to be used e.g. for errors
    if 'TERM' in os.environ:
        env['ENV']['TERM'] = os.environ['TERM']
    # Allow processes launched by scons to detect the processor architecture.
    if 'PROCESSOR_ARCHITECTURE' in os.environ:
        env['ENV']['PROCESSOR_ARCHITECTURE'] = os.environ['PROCESSOR_ARCHITECTURE']
    # Allow python processes launched by scons to honour PYTHONUNBUFFERED.
    # I think a better way of handling this would be to have each script set this itself
    # if that script is launching subprocesses, but I haven't found a good way of doing this.
    if 'PYTHONUNBUFFERED' in os.environ:
        env['ENV']['PYTHONUNBUFFERED'] = os.environ['PYTHONUNBUFFERED']
    # Prepend to the PATH env additional paths to search
    if 'PATH' in env:
        env.PrependENVPath('PATH', env['PATH'])
    # Prepend to the LD_LIBRARY_PATH env additional paths to search when executing through scons
    if 'LD_LIBRARY_PATH' in env:
        env.PrependENVPath('LD_LIBRARY_PATH', env['LD_LIBRARY_PATH'])
    # Because these path arguments may be relative, they must be correctly interpreted as relative to the top-level
    # folder rather than the 'build' subdirectory, which is what scons would do if they were passed to the SConscript
    # as-is. Therefore we convert them to absolute paths here, where they will be interpreted correctly.
    if 'CPATH' in env:
        env.AppendUnique(CPPPATH=[os.path.abspath(x) for x in env['CPATH'].split(os.pathsep)])
    if 'LPATH' in env:
        env.AppendUnique(LIBPATH=[os.path.abspath(x) for x in env['LPATH'].split(os.pathsep)])


def setup_common_env(env):
    '''
    Setup the common SConstruct build environment with default values.

    Args:
        env (SCons.Environment): The scons environment to use
    '''
    # Secure Development Lifecycle
    # The following is a set of security compilation flags required
    env.AppendUnique(CPPFLAGS=['-Werror', '-Wall', '-Wextra'])
    # Increase the warning level for 'format' to 2, but disable the nonliteral case
    env.AppendUnique(CPPFLAGS=['-Wformat=2', '-Wno-format-nonliteral'])
    env.AppendUnique(CPPFLAGS=['-Wctor-dtor-privacy', '-Woverloaded-virtual', '-Wsign-promo', '-Wstrict-overflow=2',
                               '-Wswitch-default', '-Wlogical-op', '-Wnoexcept', '-Wstrict-null-sentinel',
                               '-Wconversion'])
    # List of flags that should be set but currently fail
    # env.AppendUnique(CPPFLAGS=['-Weffc++'])
    # env.AppendUnique(CPPFLAGS=['-pedantic', '-fstack-protector-strong'])

    env.AppendUnique(CPPFLAGS=['-fPIC'])
    env.AppendUnique(CXXFLAGS=['-std=c++14'])
    if env['debug']:
        env.AppendUnique(CXXFLAGS=['-O0', '-g'])
    else:
        env.AppendUnique(CXXFLAGS=['-O3'])
    env.PrependUnique(CPPPATH=['include'])

    if env.get('coverage', False):
        env.AppendUnique(CXXFLAGS=['--coverage', '-O0'])
        env.AppendUnique(LINKFLAGS=['--coverage'])
    # By enabling this flag, binary will use RUNPATH instead of RPATH
    env.AppendUnique(LINKFLAGS=["-Wl,--enable-new-dtags"])


def setup_toolchain(env, toolchain):
    '''
    Setup the scons toolchain using predefined toolchains.

    Args:
        env (SCons.Environment): The scons environment to use
        toolchain         (str): One of the following strings are accepted ('aarch64', 'armclang', 'native')
                                 Any other value defaults to the same as native
    '''
    if toolchain == 'aarch64':
        env.Replace(CC='aarch64-linux-gnu-gcc',
                    CXX='aarch64-linux-gnu-g++',
                    LINK='aarch64-linux-gnu-g++',
                    AS='aarch64-linux-gnu-as',
                    AR='aarch64-linux-gnu-ar',
                    RANLIB='aarch64-linux-gnu-ranlib')
    elif toolchain == 'armclang':
        env.Replace(CC='armclang --target=arm-arm-none-eabi',
                    CXX='armclang --target=arm-arm-none-eabi',
                    LINK='armlink',
                    AS='armclang --target=arm-arm-none-eabi',
                    AR='armar',
                    RANLIB='armar -s')


def validate_dir(env, path, exception_type):
    '''
    Validate a directory exists, raising a specific exception in the case it is not valid.

    This is used for validating directories that cannot use the scons PathVariable validation mechanism,
    i.e. it only needs to be valid if another scons variable is set.

    Args:
        env               (SCons.Environment): The scons environment to use
        path                            (str): The scons parameter to validate
        exception_type (exceptions.Exception): The exception type to throw in the event of an invalid path
    '''
    if not os.path.isdir(env[path]):
        raise exception_type('\033[91mERROR: {} is not a valid directory.\033[0m'.format(path))


def parse_int(env, variable, exception_type):
    '''
    Validate a variable is an int, raising a specific exception in the case it is not.

    This is used for validating scons variables that should be of type int (or castable to that type).

    Args:
        env               (SCons.Environment): The scons environment to use
        variable                        (str): The scons parameter to validate
        exception_type (exceptions.Exception): The exception type to throw in the event of an invalid variable
    '''
    try:
        env[variable] = int(env[variable])
    except:
        raise exception_type('\033[91mERROR: {} is not a valid value.\033[0m'.format(variable))


def variable_exists(env, variable, exception_type):
    '''
    Check that a variable exists, raising a specific exception in the case it is not.

    This is used for validating scons variables that must be set.

    Args:
        env               (SCons.Environment): The scons environment to use
        variable                        (str): The scons parameter to validate
        exception_type (exceptions.Exception): The exception type to throw in the event of an invalid variable
    '''
    if variable not in env:
        raise exception_type('\033[91mERROR: Missing required "{}" parameter.\033[0m'.format(variable))


def abs_path(env, paths):
    '''
    Convert path(s) to their absolute path equivalent.

    Args:
        env   (SCons.Environment): The scons environment to use
        paths (str or list/tuple): The scons parameter(s) to abspath
    '''
    paths = paths if isinstance(paths, (list, tuple)) else [paths]
    for path in paths:
        try:
            env[path] = env.Dir(env[path]).abspath
        except KeyError:
            continue


def abs_filepath(env, paths):
    '''
    Convert file path(s) to their absolute file path equivalent.

    Args:
        env   (SCons.Environment): The scons environment to use
        paths (str or list/tuple): The scons parameter(s) to conviert into absolute file path
    '''
    paths = paths if isinstance(paths, (list, tuple)) else [paths]
    for path in paths:
        try:
            env[path] = env.File(env[path]).abspath
        except KeyError:
            continue
        except TypeError:
            # If path to file is not given, SCons assumes that value is '.', which is a directory
            continue


def variant_dir(env, prefix=None, suffix=None):
    '''
    Setup the scons variant_dir based on whether in debug or release mode.

    Args:
        env (SCons.Environment): The scons environment to use
        prefix  (str, optional): A prefix to the build folder
        suffix  (str, optional): A suffix to the build folder

    Returns:
        (str): The scons variant_dir
    '''
    config = 'debug' if env['debug'] else 'release'
    result = os.path.join(env['build_dir'], config)
    if prefix:
        result = os.path.join(prefix, result)
    if suffix:
        result = os.path.join(result, suffix)
    result = env.Dir(result).abspath
    env['variant_dir'] = result
    return result


def get_single_elem(elems, msg_context):
    "If a single element exists in the list, returns that. If length is not 1, it throws error"
    if len(elems) != 1:
        raise SCons.Errors.UserError('{} : Elems List size needs to be 1'.format(msg_context))
    return elems[0]


def root_dir():
    "Returns the root of driver_stack tree"
    return os.path.realpath(os.path.join(__file__, '..', '..'))


def setup_plelib_dependency(env):
    '''
    Setup plelib dependency.

    Args:
        env (SCons.Environment): The scons environment to use
    '''

    ple_include = env.get('ple_include', os.path.join(root_dir(), 'include'))

    if not os.path.exists(ple_include):
        ple_include = os.path.join(env['ple_dir'], 'build', 'release', 'include')

    # Note we *prepend* so these take priority over CPATH command-line-arguments to avoid depending on
    # the install target where the install target is also provided via CPATH.
    env.PrependUnique(CPPPATH=[ple_include])


def add_padding(align):
    '''
    Return a function that can be used in a Command target to pad a file to a multiple of align bytes in place.
    '''
    def add_padding_fn(env, source, target):
        with open(target[0].path, 'ab') as f:
            sz = f.tell()
            new_sz = ((sz + align - 1) // align) * align
            f.write(b'\x00' * (new_sz - sz))
    return add_padding_fn


def arch_regs_dir(env, variant=None):
    if variant is None:
        variant = get_single_elem(env['variants'], 'variants')

    if variant == 'fenchurch':
        return env['arch_regs_dir']

    return env['arch_regs_nx7_dir']
