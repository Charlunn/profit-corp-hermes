"""Governed credential wrapper helpers for approved project delivery."""

from __future__ import annotations


class ApprovedDeliveryGovernanceError(RuntimeError):
    """Raised when a governed credential action is invalid."""


ALLOWED_CREDENTIAL_ACTIONS = (
    "github_repository_prepare",
    "github_sync",
    "vercel_project_link",
    "vercel_env_apply",
    "vercel_deploy",
)


def run_governed_action(*, action, authority_record_path, stage, helper, **kwargs):
    raise NotImplementedError("phase 12 governance wrapper not implemented yet")
