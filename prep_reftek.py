import os, sys, glob
sys.path.append('/home/zhouyj/Documents/data_prep')
import obspy
from obspy import read, UTCDateTime
from obspy import Stream
import warnings
warnings.filterwarnings("ignore")

def date2dir(date):
    yr  = str(date.year)
    mon = str(date.month).zfill(2)
    day = str(date.day).zfill(2)
    return '%s/%s/%s'%(yr, mon, day)


# i/o paths
raw_dirs = sorted(glob.glob('/data2/201508-201603/*/2016*/*/1')) # root/sta/date/das/1/rt_files
#raw_dirs = sorted(glob.glob('/data2/201603-201702/*/2016*/*/1')) # root/sta/date/das/1/rt_files
sac_root = '/data/XJ_SAC/XLS'
start_date = UTCDateTime(2016,1,1)
end_date   = UTCDateTime(2017,1,1)
net = 'XLS'
extension = '_006DDD00'

# 1. reftek (raw dir) to sac (sac dir): r raw dir & w sac dir
# merge all reftek files and write day-long sac files
for raw_dir in raw_dirs:
    if not os.path.isdir(raw_dir): continue
    os.chdir(raw_dir)
    print(raw_dir)

    rt_files = sorted(glob.glob('*%s'%extension))
    st = Stream()
    for rt_file in rt_files:
        print('read %s' %rt_file)
        try: 
            st += read(rt_file)
            st0 = read(rt_file)
        except: obspy.io.segy.segy.SEGYTraceReadingError; print('bad data!'); continue
        n_trace = len(st0)
        if n_trace !=3: 
             print('Warning: broken trace, the program is handing gaps and overlaps!')
        # handing overlaps
        # sort
        st = st.sort(['starttime'])
        st = st.merge(method=1,fill_value=0)
    # write
    sta    = st[0].stats.station
    chn_z  = st[0].stats.channel
    chn_n  = st[1].stats.channel
    chn_e  = st[2].stats.channel
    t0     = st[0].stats.starttime
    t1     = st[-1].stats.endtime 
    # set out path
    nm1    = str(t0.year)+str(t0.month).zfill(2)+str(t0.day).zfill(2)
    out_dir = os.path.join(sac_root, sta, date2dir(date)) 
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    out_name1 = '%s.%s.%s.sac'%(sta, nm1, chn_z)
    out_name2 = '%s.%s.%s.sac'%(sta, nm1, chn_n)
    out_name3 = '%s.%s.%s.sac'%(sta, nm1, chn_e)
    out_path1 = os.path.join(out_dir, out_name1)
    out_path2 = os.path.join(out_dir, out_name2)
    out_path3 = os.path.join(out_dir, out_name3)

    st[0].slice(t0, t1).write(out_path1,format='sac')
    st[1].slice(t0, t1).write(out_path2,format='sac')
    st[2].slice(t0, t1).write(out_path3,format='sac')
    
'''
Notes: 
Stream.merge(method=1, fill_value=0, interpolation_samples=0)

1.Traces with gaps and given fill_value=0:
Trace 1: AAAA
Trace 2:         FFFF
1 + 2  : AAAA0000FFFF

2.Traces with overlaps ,discard data of the previous trace:
Trace 1: AAAAAAAA
Trace 2:     FFFFFFFF
1 + 2  : AAAAFFFFFFFF
'''
