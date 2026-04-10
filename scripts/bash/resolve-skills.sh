#!/usr/bin/env bash
# resolve-skills.sh v2.0.0 — Phase-based skill resolver (bash, no Python required)
# Usage: bash scripts/bash/resolve-skills.sh <phase> [repo_root]
#        bash scripts/bash/resolve-skills.sh --list-domain [repo_root]

SCRIPT_VERSION="2.0.0"
DEFAULT_SKILL_DIRS=("skills" ".specify/skills" ".github/skills" ".claude/skills")

# Global result arrays populated by load_adapter_skills
_SKILL_PRIORITIES=()
_SKILL_PATHS=()
_SKILL_NAMES=()
_SKILL_DESCS=()
_SKILL_INSTRUCTIONS=()

# Global parse_skill_md output vars
_SM_NAME=""
_SM_DESC=""

# ─── Utilities ───────────────────────────────────────────────────────────────

trim() {
    local s="$1"
    s="${s#"${s%%[! ]*}"}"   # remove leading whitespace
    s="${s%"${s##*[! ]}"}"   # remove trailing whitespace
    printf '%s' "$s"
}

unquote() {
    local s="$1"
    if [[ ${#s} -ge 2 ]]; then
        if [[ "${s:0:1}" == '"' && "${s: -1}" == '"' ]]; then
            s="${s:1:${#s}-2}"
        elif [[ "${s:0:1}" == "'" && "${s: -1}" == "'" ]]; then
            s="${s:1:${#s}-2}"
        fi
    fi
    printf '%s' "$s"
}

# ─── Config ──────────────────────────────────────────────────────────────────

get_skill_dirs() {
    local repo_root="$1"
    local config_path="$repo_root/.speckit.yaml"

    if [[ ! -f "$config_path" ]]; then
        for d in "${DEFAULT_SKILL_DIRS[@]}"; do
            printf '%s\n' "$repo_root/$d"
        done
        return
    fi

    local -a scan_dirs=()
    local in_skills=0 in_scan_dirs=0 cfg_version=""

    while IFS= read -r line; do
        local stripped
        stripped="$(trim "$line")"
        [[ -z "$stripped" || "${stripped:0:1}" == "#" ]] && continue

        if [[ "$line" != " "* && "$line" != $'\t'* ]]; then
            # top-level key — reset skill-section tracking
            in_skills=0
            in_scan_dirs=0
            if [[ "$stripped" == version:* ]]; then
                cfg_version="$(unquote "$(trim "${stripped#version:}")")"
            elif [[ "$stripped" == "skills:" ]]; then
                in_skills=1
            fi
        elif [[ $in_skills -eq 1 ]]; then
            if [[ "$stripped" == "scan_dirs:" ]]; then
                in_scan_dirs=1
            elif [[ $in_scan_dirs -eq 1 && "$stripped" == "- "* ]]; then
                local _d
                _d="$(trim "${stripped#- }")"
                scan_dirs+=("${_d%/}")  # strip trailing slash
            elif [[ "$stripped" != "scan_dirs:" && "$stripped" != "- "* ]]; then
                in_scan_dirs=0
            fi
        fi
    done < "$config_path"

    if [[ -n "$cfg_version" ]]; then
        local s_maj="${SCRIPT_VERSION%%.*}"
        local c_maj="${cfg_version%%.*}"
        if [[ -n "$c_maj" && "$c_maj" != "$s_maj" ]]; then
            printf 'Warning: .speckit.yaml version %s may be incompatible with resolve-skills.sh %s\n' \
                "$cfg_version" "$SCRIPT_VERSION" >&2
        fi
    fi

    if [[ ${#scan_dirs[@]} -gt 0 ]]; then
        for d in "${scan_dirs[@]}"; do
            printf '%s\n' "$repo_root/$d"
        done
        return
    fi

    for d in "${DEFAULT_SKILL_DIRS[@]}"; do
        printf '%s\n' "$repo_root/$d"
    done
}

# ─── SKILL.md Parser ─────────────────────────────────────────────────────────
# Sets globals: _SM_NAME  _SM_DESC

parse_skill_md() {
    local path="$1"
    local fallback="$2"
    _SM_NAME="$fallback"
    _SM_DESC=""

    [[ -f "$path" ]] || return

    # Read entire file into array
    local -a all_lines=()
    while IFS= read -r line; do
        all_lines+=("$line")
    done < "$path"

    # Require opening ---
    [[ "${all_lines[0]:-}" == "---" ]] || return

    # Find closing ---
    local fm_end=-1
    local i=1
    while [[ $i -lt ${#all_lines[@]} ]]; do
        if [[ "${all_lines[$i]}" == "---" ]]; then
            fm_end=$i
            break
        fi
        i=$((i + 1))
    done
    [[ $fm_end -gt 0 ]] || return

    local in_block=0
    local -a block_lines=()
    i=1
    while [[ $i -lt $fm_end ]]; do
        local line="${all_lines[$i]}"

        if [[ $in_block -eq 1 ]]; then
            if [[ -n "$line" && "$line" != " "* && "$line" != $'\t'* ]]; then
                # Block scalar ended — flush
                in_block=0
                if [[ ${#block_lines[@]} -gt 0 ]]; then
                    _SM_DESC="${block_lines[*]}"
                fi
                block_lines=()
                # Re-process this line for possible name: override
                local stripped
                stripped="$(trim "$line")"
                if [[ "$stripped" == "name:"* ]]; then
                    local val
                    val="$(unquote "$(trim "${stripped#name:}")")"
                    [[ -n "$val" ]] && _SM_NAME="$val"
                fi
            else
                local content
                content="$(trim "$line")"
                [[ -n "$content" ]] && block_lines+=("$content")
            fi
            i=$((i + 1))
            continue
        fi

        local stripped
        stripped="$(trim "$line")"

        if [[ "$stripped" == "name:"* ]]; then
            local val
            val="$(unquote "$(trim "${stripped#name:}")")"
            [[ -n "$val" ]] && _SM_NAME="$val"
        elif [[ "$stripped" == "description:"* ]]; then
            local val
            val="$(trim "${stripped#description:}")"
            if [[ "$val" == "|" || "$val" == ">" || "$val" == ">-" || "$val" == "|-" ]]; then
                in_block=1
                block_lines=()
            else
                _SM_DESC="$(unquote "$val")"
            fi
        fi
        i=$((i + 1))
    done

    # Flush any pending block at end of frontmatter
    if [[ $in_block -eq 1 && ${#block_lines[@]} -gt 0 ]]; then
        _SM_DESC="${block_lines[*]}"
    fi
}

# ─── Adapter YAML Parser ─────────────────────────────────────────────────────
# Appends matching hooks to global _SKILL_* arrays

load_adapter_skills() {
    local adapter_file="$1"
    local phase="$2"
    local skill_dir
    skill_dir="$(dirname "$adapter_file")"

    local adapter_name="Unknown"
    local in_hooks=0 has_hook=0
    local hook_phase="" hook_priority=0 hook_context=""
    local in_instructions=0 instructions_indent=0
    local -a instr_lines=()
    local hook_instructions=""

    while IFS= read -r raw_line; do
        local line="${raw_line%$'\r'}"  # strip Windows CR

        # ── Handle open instructions block ──────────────────────────────────
        if [[ $in_instructions -eq 1 ]]; then
            local stripped_l
            stripped_l="$(trim "$line")"
            # End block when: non-indented non-empty line, or new hook entry
            if [[ ( -n "$line" && "$line" != " "* && "$line" != $'\t'* ) ||
                  "$stripped_l" == "- phase:"* ]]; then
                # Flush instructions
                if [[ ${#instr_lines[@]} -gt 0 ]]; then
                    hook_instructions="$(printf '%s\n' "${instr_lines[@]}")"
                    hook_instructions="${hook_instructions%$'\n'}"
                fi
                in_instructions=0
                instructions_indent=0
                instr_lines=()
                # Fall through and re-process this line
            else
                # Detect base indent from first non-empty content line
                if [[ $instructions_indent -eq 0 && -n "$stripped_l" ]]; then
                    local no_lead="${line#"${line%%[! ]*}"}"
                    instructions_indent=$(( ${#line} - ${#no_lead} ))
                fi
                if [[ $instructions_indent -gt 0 && ${#line} -ge $instructions_indent ]]; then
                    instr_lines+=("${line:$instructions_indent}")
                else
                    instr_lines+=("$stripped_l")
                fi
                continue
            fi
        fi

        local stripped
        stripped="$(trim "$line")"
        [[ -z "$stripped" ]] && continue

        if [[ "$line" != " "* && "$line" != $'\t'* ]]; then
            # ── Top-level key ───────────────────────────────────────────────
            in_hooks=0
            if [[ "$stripped" == "name:"* ]]; then
                adapter_name="$(trim "${stripped#name:}")"
            elif [[ "$stripped" == "hooks:" ]]; then
                in_hooks=1
            fi

        elif [[ $in_hooks -eq 1 ]]; then
            # ── Inside hooks: section ───────────────────────────────────────
            if [[ "$stripped" == "- phase:"* ]]; then
                # Flush previous hook
                if [[ $has_hook -eq 1 && "$hook_phase" == "$phase" && -n "$hook_context" ]]; then
                    local ctx="$skill_dir/$hook_context"
                    if [[ -f "$ctx" ]]; then
                        parse_skill_md "$ctx" "$adapter_name"
                        _SKILL_PRIORITIES+=("$hook_priority")
                        _SKILL_PATHS+=("$ctx")
                        _SKILL_NAMES+=("$_SM_NAME")
                        _SKILL_DESCS+=("$_SM_DESC")
                        _SKILL_INSTRUCTIONS+=("$hook_instructions")
                    fi
                fi
                # Start new hook
                has_hook=1
                hook_phase="$(trim "${stripped#- phase:}")"
                hook_priority=0
                hook_context=""
                hook_instructions=""
                in_instructions=0
                instructions_indent=0
                instr_lines=()

            elif [[ $has_hook -eq 1 ]]; then
                if [[ "$stripped" == "priority:"* ]]; then
                    hook_priority="$(trim "${stripped#priority:}")"
                elif [[ "$stripped" == "context:"* ]]; then
                    hook_context="$(trim "${stripped#context:}")"
                elif [[ "$stripped" == "instructions:"* ]]; then
                    local val
                    val="$(trim "${stripped#instructions:}")"
                    if [[ "$val" == "|" || "$val" == ">" ]]; then
                        in_instructions=1
                        instructions_indent=0
                        instr_lines=()
                    else
                        hook_instructions="$val"
                    fi
                fi
            fi
        fi
    done < "$adapter_file"

    # Flush any trailing open instructions block
    if [[ $in_instructions -eq 1 && ${#instr_lines[@]} -gt 0 ]]; then
        hook_instructions="$(printf '%s\n' "${instr_lines[@]}")"
        hook_instructions="${hook_instructions%$'\n'}"
    fi

    # Flush last hook
    if [[ $has_hook -eq 1 && "$hook_phase" == "$phase" && -n "$hook_context" ]]; then
        local ctx="$skill_dir/$hook_context"
        if [[ -f "$ctx" ]]; then
            parse_skill_md "$ctx" "$adapter_name"
            _SKILL_PRIORITIES+=("$hook_priority")
            _SKILL_PATHS+=("$ctx")
            _SKILL_NAMES+=("$_SM_NAME")
            _SKILL_DESCS+=("$_SM_DESC")
            _SKILL_INSTRUCTIONS+=("$hook_instructions")
        fi
    fi
}

# ─── Commands ────────────────────────────────────────────────────────────────

cmd_list_domain() {
    local repo_root="$1"
    local -a skill_dirs=()
    mapfile -t skill_dirs < <(get_skill_dirs "$repo_root")

    local found=0
    declare -A seen_names=()

    for skills_dir in "${skill_dirs[@]}"; do
        [[ -d "$skills_dir" ]] || continue
        for skill_path in "$skills_dir"/*/; do
            [[ -d "$skill_path" ]] || continue
            local skill_md="$skill_path/SKILL.md"
            local adapter="$skill_path/speckit-adapter.yaml"
            [[ -f "$skill_md" ]] || continue
            [[ -f "$adapter" ]] && continue  # skip adapter-backed skills

            parse_skill_md "$skill_md" "$(basename "${skill_path%/}")"

            if [[ -z "${seen_names[$_SM_NAME]+x}" ]]; then
                seen_names["$_SM_NAME"]=1
                local disp_desc="${_SM_DESC:-"(no description)"}"
                printf -- '- **%s**: %s\n' "$_SM_NAME" "$disp_desc"
                found=1
            fi
        done
    done

    if [[ $found -eq 0 ]]; then
        echo "_No domain skills found in configured scan directories._"
    fi
}

cmd_phase() {
    local phase="$1"
    local repo_root="$2"
    local -a skill_dirs=()
    mapfile -t skill_dirs < <(get_skill_dirs "$repo_root")

    for skills_dir in "${skill_dirs[@]}"; do
        [[ -d "$skills_dir" ]] || continue
        for adapter_file in "$skills_dir"/*/speckit-adapter.yaml; do
            [[ -f "$adapter_file" ]] || continue
            load_adapter_skills "$adapter_file" "$phase"
        done
    done

    local count="${#_SKILL_PRIORITIES[@]}"

    if [[ $count -eq 0 ]]; then
        printf '<active_skills phase="%s" count="0">\n' "$phase"
        printf '  <directive>No specialist skills are configured for this phase. Proceed with general best practices.</directive>\n'
        printf '</active_skills>\n'
        return
    fi

    # Sort indices by priority descending
    local -a sort_pairs=()
    local i=0
    while [[ $i -lt $count ]]; do
        sort_pairs+=("${_SKILL_PRIORITIES[$i]}|$i")
        i=$((i + 1))
    done

    local -a sorted_indices=()
    while IFS='|' read -r _ idx; do
        sorted_indices+=("$idx")
    done < <(printf '%s\n' "${sort_pairs[@]}" | sort -t'|' -k1 -rn)

    printf '<active_skills phase="%s" count="%s">\n' "$phase" "$count"
    printf "  <directive>The following specialist skills are active for this phase. You MUST read each skill's persona_file and fully adopt its persona and workflows before proceeding.</directive>\n"

    for idx in "${sorted_indices[@]}"; do
        local name="${_SKILL_NAMES[$idx]}"
        local desc="${_SKILL_DESCS[$idx]}"
        local path="${_SKILL_PATHS[$idx]}"
        local instructions="${_SKILL_INSTRUCTIONS[$idx]}"

        printf '\n  <skill name="%s">\n' "$name"
        if [[ -n "$desc" ]]; then
            printf '    <description>%s</description>\n' "$desc"
        fi
        printf '    <persona_file>%s</persona_file>\n' "$path"
        if [[ -n "$instructions" ]]; then
            printf '    <integration>\n'
            printf '%s\n' "$instructions"
            printf '    </integration>\n'
        fi
        printf '  </skill>\n'
    done

    printf '\n</active_skills>\n'
}

# ─── Entry Point ─────────────────────────────────────────────────────────────

if [[ $# -lt 1 ]]; then
    printf 'Usage: resolve-skills.sh <phase> [repo_root]\n' >&2
    printf '       resolve-skills.sh --list-domain [repo_root]\n' >&2
    exit 1
fi

PHASE="$1"
REPO_ROOT="${2:-$PWD}"

if [[ "$PHASE" == "--list-domain" ]]; then
    cmd_list_domain "$REPO_ROOT"
else
    cmd_phase "$PHASE" "$REPO_ROOT"
fi
