echo "DEMO STARTING"; echo "hurricane" > model.txt; source ../venv/bin/activate; python LaunchManager.py; sleep 1; python WindowManager.py; sleep 1; python AlignmentManager.py; sleep 1; python SamplingManager.py; sleep 1; python ExecutionManager.py; sleep 5; python ExecutionManager.py; sleep 1; python PostSynchronizationManager.py; sleep 1; python OutputManager.py; sleep 1; echo "flood" > model.txt; python WindowManager.py; sleep 1; python AlignmentManager.py; sleep 1; python SamplingManager.py; sleep 1; python ExecutionManager.py; sleep 15; python ExecutionManager.py; sleep 1; python PostSynchronizationManager.py; sleep 1; python OutputManager.py; sleep 1; echo "DEMO COMPLETE"