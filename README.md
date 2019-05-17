# SeisFlows-devel
Add new functions to SeisFlows

1. ./seisflows/plugins/adjoint.py 
	Envelope, avoid divide zero when mute near-offset data.
2. ./seisflows/tools/signal.py
	Apply tapered mask to shot gather, muting body waves and later waves to preserve surface wave.
3. Fixed some bugs in RTM. The original code failed to get correct adjoint source
