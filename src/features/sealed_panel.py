"""Read only a permitted column prefix from NPZ target rows.

Unlike load_panel(through=...), future target cells are never decoded into arrays.
ZIP seek may traverse compressed bytes; it does not interpret skipped target values.
"""
from zipfile import ZipFile
import numpy as np
from features.panel import Panel

VALIDATION_CUTOFF='2022-10'


def target_prefix(stream,stop,rows,columns):
    version=np.lib.format.read_magic(stream)
    if version==(1,0):shape,fortran,dtype=np.lib.format.read_array_header_1_0(stream)
    elif version==(2,0):shape,fortran,dtype=np.lib.format.read_array_header_2_0(stream)
    else:raise ValueError('Unsupported sealed target format')
    if shape!=(rows,columns) or dtype.hasobject or dtype.kind!='f':raise ValueError('Expected floating target matrix')
    if not 0<stop<=columns:raise ValueError('Invalid target prefix')
    if fortran:
        data=stream.read(rows*stop*dtype.itemsize)
        if len(data)!=rows*stop*dtype.itemsize:raise ValueError('Truncated column-major target prefix')
        return np.frombuffer(data,dtype=dtype).reshape((rows,stop),order='F').copy()
    start=stream.tell();result=np.empty((rows,stop),dtype=dtype)
    for row in range(rows):
        stream.seek(start+row*columns*dtype.itemsize)
        data=stream.read(stop*dtype.itemsize)
        if len(data)!=stop*dtype.itemsize:raise ValueError('Truncated target prefix')
        result[row]=np.frombuffer(data,dtype=dtype,count=stop)
    return result


def load_prefix(path,through,permit=None):
    if str(through)>VALIDATION_CUTOFF:
        if permit is None or not permit.signature or str(through)>permit.max_month:
            raise RuntimeError('Sealed targets require tagged final-test authorisation BEFORE opening the panel')
    with np.load(path,allow_pickle=False) as data:
        codes=data['codes'].copy();months=data['months'].copy();observed=data['observed'].copy();edges=data['edges'].copy()
    positions=np.flatnonzero(months==str(through))
    if len(positions)!=1:raise ValueError('Requested month absent')
    stop=int(positions[0])+1
    with ZipFile(path) as archive:
        with archive.open('targets.npy') as stream:targets=target_prefix(stream,stop,len(codes),len(months))
    if not np.isfinite(targets[observed]).all() or (targets[observed]<0).any():raise ValueError('Invalid observed target history')
    if np.isfinite(targets[~observed]).any():raise ValueError('Unknown targets were changed')
    return Panel(codes,months[:stop],targets,observed,edges)
