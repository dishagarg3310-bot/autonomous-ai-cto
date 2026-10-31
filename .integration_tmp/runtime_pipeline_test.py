import json
from pathlib import Path

from modules.m08_sandbox.executor import DockerExecutor
from modules.m09_qa.runner import QARunner
from modules.m10_interaction.progress import create_progress_event


ROOT = Path(r"C:\Users\abina\autonomous-ai-cto")
APP = ROOT / "ai-cto-task2" / "backend" / "generated_backend"
FAILURE_PROJECT = ROOT / ".integration_tmp" / "failure_project"
IMPORT_COMMAND = [
    "python",
    "-c",
    "import os; os.environ['SECRET_KEY']='integration-test-only'; os.environ['DATABASE_URL']='sqlite:////tmp/app.db'; import main; print('application_import_ok')",
]


def execution_evidence(result):
    return {
        "execution_id": result.execution_id,
        "project_id": result.project_id,
        "task_id": result.task_id,
        "status": result.status,
        "exit_code": result.exit_code,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "duration_ms": result.duration_ms,
        "error_type": result.error_type,
    }


def report_evidence(report):
    return {
        "report_id": report.report_id,
        "execution_id": report.execution_id,
        "project_id": report.project_id,
        "task_id": report.task_id,
        "status": report.status,
        "issues_found": report.issues_found,
        "issues": report.issues,
        "bugs": [bug.model_dump() for bug in report.bugs],
        "stdout": report.stdout.strip(),
        "stderr": report.stderr.strip(),
        "duration_ms": report.duration_ms,
    }


executor = DockerExecutor(image="ai-cto-generated-backend:test", timeout_seconds=30)
m08_success = executor.execute(
    project_path=APP,
    command=IMPORT_COMMAND,
    project_id="integration-project",
    task_id="m06-m08-import",
)

qa_runner = QARunner(executor=executor)
m09_success = qa_runner.run(
    project_path=APP,
    command=IMPORT_COMMAND,
    project_id="integration-project",
    task_id="m08-m09-import",
)

m09_failure = qa_runner.run(
    project_path=FAILURE_PROJECT,
    command=["python", "failure_probe.py"],
    project_id="integration-project",
    task_id="m09-controlled-failure",
)

m10_event = create_progress_event(
    execution_id=m09_failure.execution_id or "missing-execution-id",
    project_id=m09_failure.project_id,
    task_id=m09_failure.task_id,
    status="failed" if m09_failure.status == "failed" else "escalated",
    message=f"M09 completed with status {m09_failure.status}; issues={m09_failure.issues_found}",
    attempt_number=1,
)

print(json.dumps({
    "m06_to_m08": execution_evidence(m08_success),
    "m08_to_m09": report_evidence(m09_success),
    "m09_failure_classification": report_evidence(m09_failure),
    "m09_to_m10": m10_event.model_dump(mode="json"),
}, indent=2))
