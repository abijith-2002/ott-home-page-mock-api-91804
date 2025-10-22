#!/bin/bash
cd /home/kavia/workspace/code-generation/ott-home-page-mock-api-91804/backend_mock_api
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

