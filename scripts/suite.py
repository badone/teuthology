import docopt
import sys

import teuthology.suite
from teuthology.suite import override_arg_defaults as defaults
from teuthology.config import config

doc = """
usage: teuthology-suite --help
       teuthology-suite [-v | -vv ] --suite <suite> [options] [<config_yaml>...]
       teuthology-suite [-v | -vv ] --rerun <name>  [options] [<config_yaml>...]

Run a suite of ceph integration tests. A suite is a directory containing
facets. A facet is a directory containing config snippets. Running a suite
means running teuthology for every configuration combination generated by
taking one config snippet from each facet. Any config files passed on the
command line will be used for every combination, and will override anything in
the suite. By specifying a subdirectory in the suite argument, it is possible
to limit the run to a specific facet. For instance -s upgrade/dumpling-x only
runs the dumpling-x facet of the upgrade suite.

Miscellaneous arguments:
  -h, --help                  Show this help message and exit
  -v, --verbose               Be more verbose
  --dry-run                   Do a dry run; do not schedule anything. In
                              combination with -vv, also call
                              teuthology-schedule with --dry-run.
  -y, --non-interactive       Do not ask question and say yes when
                              it is possible.

Standard arguments:
  <config_yaml>               Optional extra job yaml to include
  -s <suite>, --suite <suite>
                              The suite to schedule
  --wait                      Block until the suite is finished
  -c <ceph>, --ceph <ceph>    The ceph branch to run against
                              [default: {default_ceph_branch}]
  -S <sha1>, --sha1 <sha1>    The ceph sha1 to run against (overrides -c)
                              If both -S and -c are supplied, -S wins, and
                              there is no validation that sha1 is contained
                              in branch
  -n <newest>, --newest <newest>
                              Search for the newest revision built on all
                              required distro/versions, starting from
                              either --ceph or --sha1, backtracking
                              up to <newest> commits [default: 0]
  -k <kernel>, --kernel <kernel>
                              The kernel branch to run against,
                              use 'none' to bypass kernel task.
                              [default: distro]
  -f <flavor>, --flavor <flavor>
                              The kernel flavor to run against: ('basic',
                              'gcov', 'notcmalloc')
                              [default: basic]
  -t <branch>, --teuthology-branch <branch>
                              The teuthology branch to run against.
                              Default value is determined in the next order.
                              There is TEUTH_BRANCH environment variable set.
                              There is `qa/.teuthology_branch` present in
                              the suite repo and contains non-empty string.
                              There is `teuthology_branch` present in one of
                              the user or system `teuthology.yaml` configuration
                              files respectively, otherwise use `master`.
  -m <type>, --machine-type <type>
                              Machine type [default: {default_machine_type}]
  -d <distro>, --distro <distro>
                              Distribution to run against
  -D <distroversion>, --distro-version <distroversion>
                              Distro version to run against
  --ceph-repo <ceph_repo>     Query this repository for Ceph branch and SHA1
                              values [default: {default_ceph_repo}]
  --suite-repo <suite_repo>   Use tasks and suite definition in this repository
                              [default: {default_suite_repo}]
  --suite-relpath <suite_relpath>
                              Look for tasks and suite definitions in this
                              subdirectory of the suite repo.
                              [default: qa]
  --suite-branch <suite_branch>
                              Use this suite branch instead of the ceph branch
  --suite-dir <suite_dir>     Use this alternative directory as-is when
                              assembling jobs from yaml fragments. This causes
                              <suite_branch> to be ignored for scheduling
                              purposes, but it will still be used for test
                              running. The <suite_dir> must have `qa/suite`
                              sub-directory.
  --validate-sha1 <bool>
                              Validate that git SHA1s passed to -S exist.
                              [default: true]
  --sleep-before-teardown <seconds>
                              Number of seconds to sleep before teardown.
                              Use with care, as this applies to all jobs in the
                              run. This option is used along with --limit one.
                              If the --limit ommitted then it's forced to 1.
                              If the --limit is greater than 4, then user must
                              confirm it interactively to avoid massive lock
                              of resources, however --non-interactive option
                              can be used to skip user input.
                              [default: 0]
  --arch <arch>               Override architecture defaults, for example,
                              aarch64, armv7l, x86_64. Normally this
                              argument should not be provided and the arch
                              is determined from --machine-type.

Scheduler arguments:
  --owner <owner>             Job owner
  -b <backend>, --queue-backend <backend>
                              Scheduler queue backend name
  -e <email>, --email <email>
                              When tests finish or time out, send an email
                              here. May also be specified in ~/.teuthology.yaml
                              as 'results_email'
  --rocketchat <rocketchat>   Comma separated list of Rocket.Chat channels where
                              to send a message when tests finished or time out.
                              To be used with --sleep-before-teardown option.
  -N <num>, --num <num>       Number of times to run/queue the job
                              [default: 1]
  -l <jobs>, --limit <jobs>   Queue at most this many jobs
                              [default: 0]
  --subset <index/outof>      Instead of scheduling the entire suite, break the
                              set of jobs into <outof> pieces (each of which will
                              contain each facet at least once) and schedule
                              piece <index>.  Scheduling 0/<outof>, 1/<outof>,
                              2/<outof> ... <outof>-1/<outof> will schedule all
                              jobs in the suite (many more than once).
  -p <priority>, --priority <priority>
                              Job priority (lower is sooner)
                              [default: 1000]
  --timeout <timeout>         How long, in seconds, to wait for jobs to finish
                              before sending email. This does not kill jobs.
                              [default: {default_results_timeout}]
  --filter KEYWORDS           Only run jobs whose description contains at least one
                              of the keywords in the comma separated keyword
                              string specified.
  --filter-out KEYWORDS       Do not run jobs whose description contains any of
                              the keywords in the comma separated keyword
                              string specified.
  --filter-all KEYWORDS       Only run jobs whose description contains each one
                              of the keywords in the comma separated keyword
                              string specified.
  -F, --filter-fragments <bool>
                              Check yaml fragments too if job description
                              does not match the filters provided with
                              options --filter, --filter-out, and --filter-all.
                              [default: false]
  --archive-upload RSYNC_DEST Rsync destination to upload archives.
  --archive-upload-url URL    Public facing URL where archives are uploaded.
  --throttle SLEEP            When scheduling, wait SLEEP seconds between jobs.
                              Useful to avoid bursts that may be too hard on
                              the underlying infrastructure or exceed OpenStack API
                              limits (server creation per minute for instance).
  -r, --rerun <name>          Attempt to reschedule a run, selecting only those
                              jobs whose status are mentioned by
                              --rerun-status.
                              Note that this is implemented by scheduling an
                              entirely new suite and including only jobs whose
                              descriptions match the selected ones. It does so
                              using the same logic as --filter.
                              Of all the flags that were passed when scheduling
                              the original run, the resulting one will only
                              inherit the suite value. Any others must be
                              passed as normal while scheduling with this
                              feature. For random tests involving facet whose
                              path ends with '$' operator, you might want to
                              use --seed argument to repeat them.
 -R, --rerun-statuses <statuses>
                              A comma-separated list of statuses to be used
                              with --rerun. Supported statuses are: 'dead',
                              'fail', 'pass', 'queued', 'running', 'waiting'
                              [default: fail,dead]
 --seed SEED                  An random number mostly useful when used along
                              with --rerun argument. This number can be found
                              in the output of teuthology-suite command. -1
                              for a random seed [default: -1].
 --force-priority             Skip the priority check.
 --job-threshold <threshold>  Do not allow to schedule the run if the number
                              of jobs exceeds <threshold>. Use 0 to allow
                              any number [default: {default_job_threshold}].

""".format(
    default_machine_type=config.default_machine_type,
    default_results_timeout=config.results_timeout,
    default_ceph_repo=defaults('--ceph-repo',
                            config.get_ceph_git_url()),
    default_suite_repo=defaults('--suite-repo',
                            config.get_ceph_qa_suite_git_url()),
    default_ceph_branch=defaults('--ceph-branch', 'master'),
    default_job_threshold=config.job_threshold,
)


def main(argv=sys.argv[1:]):
    args = docopt.docopt(doc, argv=argv)
    return teuthology.suite.main(args)
