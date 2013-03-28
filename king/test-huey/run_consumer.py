import pkg_resources, os, sys

current_dir = os.getcwd()
sys.path.append(current_dir)

__requires__ = 'huey==0.3.2'
import pkg_resources
pkg_resources.run_script('huey==0.3.2', 'huey_consumer.py')
