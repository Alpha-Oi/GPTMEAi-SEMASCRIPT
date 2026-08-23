# SEMASCRIPT Adapter

This adapter normalizes SEMASCRIPT parser, AST, or action-document output into
the canonical `semascript_action_document` contract.

v0.1 accepts already-normalized documents and provides a conservative AST
normalizer. It does not run SEMASCRIPT tooling or mutate SEMASCRIPT state.
