"""Run one named natural CPU job, permitting short base jobs before long extras."""
import argparse
from models.screen_cpu import initialise,extra_jobs,base_jobs,full_jobs,choose_extras,execute,assemble_base,assemble_full,folder


def main():
    parser=argparse.ArgumentParser(__doc__); parser.add_argument('--name',required=True); args=parser.parse_args()
    cfg=initialise(); selection=choose_extras()
    jobs={j['name']:j for j in extra_jobs()+base_jobs()+full_jobs(cfg,selection)}
    if args.name not in jobs:raise ValueError('Unknown job')
    execute(jobs[args.name],cfg)
    selection=choose_extras(); assemble_full(cfg,selection)
    if all((folder(j)/'complete.json').exists() for j in base_jobs()):assemble_base()


if __name__=='__main__':main()
