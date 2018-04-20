import os, re

#strings that we are looking for
sp = re.compile('ERROR:|UNINI|WARNING',flags=re.IGNORECASE)

def dir(path):
    """
    Used to check SAS logs for errors in a specified folder (with regex)
    """
    for f in os.listdir(path):
        tf = open(path + f, 'r')
        ft = tf.read()
        tf.close()
        matches = re.findall(sp, ft)
        if matches:
            print '    > ' + f.upper() + ' IS DIRTY:'
            for i, line in enumerate(open(path + f)):
                for match in re.finditer(sp, line):
                    print '      > Line %s - %s' % (i+1,' '.join(line.split()))
        else:
            print '    > ' + f + ' is clean'

    return None

def path(path):
    """
    Used to check a single SAS log for errors (with regex)
    """
    tf = open(path, 'r')
    ft = tf.read()
    tf.close()
    matches = re.findall(sp, ft)
    if matches:
        print '    > ' + path.upper() + ' IS DIRTY:'
        for i, line in enumerate(open(path)):
            for match in re.finditer(sp, line):
                print '      > Line %s - %s' % (i+1,' '.join(line.split()))
    else:
        print '    > ' + path + ' is clean'

    return None