#!/usr/bin/env python
import os
from multiprocessing.pool import ThreadPool

import argparse
import numpy
#from scipy import stats

def getNormalDist(args):
    # This is a uniform distribution, normal was not working out like I expected
    return numpy.random.uniform(args.min, args.max, args.files)
#    return stats.truncnorm(
#        a=(args.min - args.avg) / args.std,
#        b=(args.max - args.avg) / args.std,
#        loc=args.avg, scale=args.std).rvs(args.files)

def getBytes(val):
    digits = []
    units = ''
    validUnits = ('K', 'M', 'G', 'T')
    unitFactor = (1e3, 1e6, 1e9, 1e12)
    unitIdx = 0
    for idx, x in enumerate(val):
        try:
            int(x)
        except ValueError:
            units = val[idx:]
        else:
            digits.append(x)
    if len(units) > 1:
        raise Exception('size units must be a single character ({0})'.format(', '.join(validUnits)))
    if units and units.upper() not in validUnits:
        raise Exception('unrecognized size unit: {0}, must be one of ({1})'.format(units, ', '.join(validUnits)))
    ret = int(''.join(digits))
    if units:
        ret = ret * unitFactor[validUnits.index(units.upper())]
    return ret

def getargs():
    p = argparse.ArgumentParser(conflict_handler='resolve')
    p.add_argument('-l', '--min', help='Minimum file size (bytes or appropriate unit; 1K, 2M)', default='1')
    p.add_argument('-h', '--max', help='Maximum file size (bytes or appropriate unit; 1K, 2M)', default='100M')
#    p.add_argument('-a', '--avg', help='Average file size (bytes or appropriate unit; 1K, 2M)', default='0')
#    p.add_argument('-s', '--std', help='Standard deviation', type=int, default=1)
    p.add_argument('-f', '--files', help='Number of files to generate', type=int, default='10000')
    p.add_argument('-t', '--threads', help='Number of threads to spawn (defaults to OS cpu_count)', type=int, default=0)
    p.add_argument('--skeleton', help='Only create the file skeleton of size without writing any data', action='store_true')
    p.add_argument('-m', '--mask', help='Create a subdirectory structure of each file based on it\'s name. '\
        'Mask should use an x character to denote a digit of the filename. The default of no mask puts each '\
        'file as a uniquely named file in a single output directory', default=None)
    p.add_argument('-o', '--output', help='Output path to write files to')
    p.add_argument('-r', '--root', help='Root directory name containing any masked subdirectories',
        default='plopperFiles')
    args = p.parse_args()
    try:
        args.min = getBytes(args.min)
        args.max = getBytes(args.max)
#        if args.avg == '0':
#            args.avg = str(int((args.max - args.min) / 2 + args.min))
#        args.avg = getBytes(args.avg)
    except Exception as e:
        p.error(e)
#    if args.max < args.min or args.max < args.avg or args.min > args.avg:
#        p.error('min/avg/max values must be numerically sequential')
    if args.max < args.min:
        p.error('min/max values must be numerically sequential')
    if args.files <= 0:
        p.error('--files argument must be greater than 0')
    if args.threads <= 0:
        args.threads = None
    if not args.output:
        args.output = os.getcwd()
    elif not os.path.exists(args.output):
        p.error('Invalid output directory, please create it first')
    args.output = os.path.join(args.output, args.root)
    if not os.path.exists(args.output):
        try:
            os.makedirs(args.output)
        except Exception as e:
            p.error('Failed to create output directory: {0}'.format(e))
    if args.mask:
        args.mask = ''.join([m.lower() for m in args.mask])
        count = args.mask.count('x')
        if count < len(str(args.files)):
            args.mask = os.path.join('{0}'.format('x' * (len(str(args.files)) - count)), '{0}'.format(args.mask))
            print('Mask length insufficient for number of files, automatically enlarging mask => {0}'.format(args.mask))
    return args

def plopFile(root, mask, name, size, skeleton, results):
    if mask:
        # mask = 'xxx/xxx/xxx/x.dat'
        maskDigits = [c for c in mask if c == 'x']
        # maskDigits = 10
        nameMask = list(name.zfill(len(maskDigits)))
        # name = '35'
        # nameMask = '0000000035'
        fMask = []
        for m in mask:
            if m == 'x':
                fMask.append(nameMask[0])
                nameMask.remove(nameMask[0])
            else:
                fMask.append(m)
        # fMask = '000/000/003/5.dat'
    else:
        fMask = [name]
    filePath = os.path.join(root, ''.join(fMask))
    dirName = os.path.dirname(filePath)
    if not os.path.exists(dirName):
        try:
            os.makedirs(dirName)
        except FileExistsError:
            pass
    def bySeek():
        with open(filePath, 'wb') as fp:
            if skeleton:
                fp.seek(size - 1)
                fp.write(b'\0')
            else:
                fp.write(b'\0' * size)

    if skeleton and hasattr(os, 'truncate'):
        try:
            with open(filePath, 'wb') as fp:
                fp.truncate(size)
        except Exception:
            bySeek()
    else:
        bySeek()
    results['totalFiles'] += 1
    results['totalBytes'] += size

def main():
    args = getargs()
    values = getNormalDist(args)
    results = {
        'totalBytes': 0,
        'totalFiles': 0
    }
    print('Writing {0} for {1} files with a size range of {2} to {3} bytes to {4}'.format(
        'skeletons' if args.skeleton else 'data', args.files, args.min, args.max,
        args.output))
    pool = ThreadPool(args.threads)
    for idx, val in enumerate(values, start=1):
        pool.apply_async(plopFile, (args.output, args.mask, str(idx), int(val), args.skeleton, results))
    pool.close()
    pool.join()
    print('Complete, {0} files written'.format(results['totalFiles']))
    print('Total bytes {0}written{0}: {1}'.format('"' if args.skeleton else '', results['totalBytes']))

if __name__ == '__main__':
    main()

