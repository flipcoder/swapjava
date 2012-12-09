#!/usr/bin/python2
import sh, os, sys

def confirm(question, default="y"):
    default = default.lower()
    if default=="y":
        options="Y/n"
    else:
        options="y/N"
    choice = raw_input("%s (%s)? " % (question, options))
    choice = choice.lower()
    if choice == "":
        choice = default
    return choice=="y"


def menu_print(msg):
    print msg

def menu(title, msg, options, back=False, back_text="Back", index=True, current="", current_append=" (current)", print_func=menu_print, input_func=raw_input):
    """
    Builds text menu with title, message, and options
    'back' refers to if the menu should allow Back option
    'index' to whether or not value returned should be only index (otherwise it'll return actual option or 'None')
    'current' is an optional highlighted option
    'current_append' is the message to be appended to the highlighted option
    """

    while True:
        choice = 0
        i = 1
        print_func("%s" % title)
        for m in options:
            append = ""
            if current==m:
                append = current_append
            print_func("%s. %s%s" % (i,m,append))
            i += 1
        if back:
            print_func("%s. [ %s ]" % (i, back_text))
        try:
            choice = int(input_func(msg))
        except TypeError:
            continue # loop again
        except ValueError:
            continue
        if choice > 0 and choice <= len(options):
            break
        elif choice == len(options)+1:
            if back:
                return -1 if index else None 
            else:
                continue
    if not index:
        if choice != -1:
            return options[choice-1]
        else:
            return None
    return choice-1


def main():
    current_jvm_guess = ""

    JVM_DIR = "/usr/lib/jvm/"
    BIN_DIR = "/usr/bin"

    # add more here as you need (this is safer than scanning the bin directory)
    java_utils = [
        "java",
        "javac",
        "javadoc",
        "jar",
        "jarsigner",
        "jdb",
        "keytool",
    ]
    jvm_installs = {}

    if os.path.islink(os.path.join(BIN_DIR, "java")):
        END_DIR = "/bin/java"
        current_jvm_guess = os.readlink(os.path.join(BIN_DIR, "java"))
        if current_jvm_guess.startswith(JVM_DIR) and current_jvm_guess.endswith(END_DIR):
            current_jvm_guess = current_jvm_guess[len(JVM_DIR):-len(END_DIR)] # chop off start

    # scan for java installations in JVM_DIR (set above)
    for f in os.listdir(JVM_DIR):
        full = os.path.join(JVM_DIR, f)
        if os.path.isdir(full):
            jvm_installs[f] = full

    if not jvm_installs:
        print "No Java installations in %s" % JVM_DIR
        return 1

    # menu
    try:
        jvm_selection = menu("Java selection", "select a number: ", jvm_installs.keys(), back=True, back_text="Exit", index=False, current=current_jvm_guess)
    except KeyboardInterrupt:
        return 0
    if not jvm_selection:
        return 0

    jvm_selection = jvm_installs[jvm_selection] # get full path
    java_bin_path = os.path.join(jvm_selection,"bin")

    # [UNSAFE] scan the bin directory for every program
    #for f in os.listdir(java_bin_path):
    #    full = os.path.join(java_bin_path, f)
    #    if os.path.isfile(full) and  os.access(full, os.X_OK) and not os.islink(full):
    #        java_utils += [f]

    # create symlinks
    sh.cd(BIN_DIR)
    for util in java_utils:
        link_path = os.path.join(BIN_DIR,util)
        util_path = os.path.join(java_bin_path, util)
        print "Installing %s..." % util
        if os.path.isfile(link_path) and confirm("Replace %s" % util):
            os.unlink(link_path)
        try:
            sh.ln('-s', os.path.join(java_bin_path, util), util) # cd needed for this line
        except sh.ErrorReturnCode_1:
            print "You need root permissions (didn't use sudo?)."
            return 1
        print "%s installed." % util


if __name__=="__main__":
    sys.exit(main())

