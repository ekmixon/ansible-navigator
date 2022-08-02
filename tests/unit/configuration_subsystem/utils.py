"""Utility functions used by adjacent tests
"""

from ansible_navigator.configuration_subsystem.definitions import Entry


def id_for_base(val):
    """Return an id for a param set."""
    if val is None:
        return "No base params"
    if "editor-command" in val:
        return "Long base params"
    return "Short base params" if "ecmd" in val else "Unknown base params"


def id_for_cli(val):
    """Generate an id for a CLI entry."""
    return val if isinstance(val, str) else ""


def id_for_name(val):
    """Return an id based on entry name."""
    return f" {val.name} " if isinstance(val, Entry) else ""


def id_for_settings(val):
    """Generate an id for a settings entry."""
    if val in ["DEFAULT_CFG", "USER_CFG"]:
        return f"others={val}"
    if val == "ansible-navigator_empty.yml":
        return "empty settings file"
    return "full settings file" if val == "ansible-navigator.yml" else val


def config_post_process(expected, path):
    """Perform custom post processing on the configuration."""
    if path == "ansible-navigator.execution-environment.volume-mounts":
        parsed_volume_mounts = []
        volume_mounts = expected["ansible-navigator"]["execution-environment"]["volume-mounts"]
        for volume_mount in volume_mounts:
            mount_path = f"{volume_mount['src']}:{volume_mount['dest']}"
            if volume_mount.get("label"):
                mount_path += f":{volume_mount['label']}"
            parsed_volume_mounts.append(mount_path)
        expected["ansible-navigator"]["execution-environment"][
            "volume-mounts"
        ] = parsed_volume_mounts

    return expected
