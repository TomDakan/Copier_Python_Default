# Template v1 To-Do List

## Step 4: Implement simple task tracking alternative option
- [ ] **Update Copier questions:** Update question that asks about creating to github project so that it supports 3 choices: "Configure task tracking for this project? TODO.md, Github Projects, none" default: TODO.md.
- [ ] **Update copier scripts and tools:** make any necessary changes to support the new option for task tracking including adding a TODO.md.jinja file.

## 🚀 Step 5: Optional CI/CD & Dependency Management

- [ ] **GitHub Push & Account:** Add `push_to_github` and `github_account` questions.
- [ ] **Semantic Release:** Ensure `use_semantic_release` question and conditional workflow exclusions/dependency additions.
- [ ] **Dependabot:**
    - [ ] Add `use_dependabot` and `dependabot_automerge` questions to `copier.yaml`.
    - [ ] Scaffold `.github/dependabot.yml.jinja` with conditional `automerge: true`.
    - [ ] Add test: `test_with_dependabot_automerge`.
- [ ] **Scaffold Workflows:** Ensure all `.github/workflows/` files are correctly scaffolded and use conditional logic.

## 💻 Step 6: Optional Developer Experience Features

- [ ] **`.env` File Generation:**
    - [ ] Add `generate_env` boolean question to `copier.yaml`.
    - [ ] Ensure `.env.jinja` exists and is conditionally excluded.
    - [ ] Ensure `test_with_env_file` exists.

## 🏛️ Step 7: Optional Project Management & Documentation Features

- [ ] **Automate ADR Creation:**
    - [ ] Add `include_adr` boolean question to `copier.yaml`.
    - [ ] Scaffold `scripts/new_adr.py`.
    - [ ] Scaffold `docs/adr/0000-template.md`.
    - [ ] Ensure conditional inclusion in `scripts`.
    - [ ] Add exclusion rules.
    - [ ] Add test: `test_with_adr_support`.
- [ ] **Implement GitHub Project Scaffolding:**
    - [ ] Add `create_github_project` boolean question to `copier.yaml`.
    - [ ] Ensure `bootstrap.py` exists and receives the argument in `_tasks`.
    - [ ] Add test: `test_with_github_project`.
- [ ] **Integrate `ROADMAP.md` and GitHub Project:**
    - [ ] Scaffold `ROADMAP.md.jinja` with placeholder.
    - [ ] Ensure `bootstrap.py` logic updates the placeholder.
    - [ ] Ensure test `test_with_github_project` checks for the placeholder.
- [ ] **Add Repository Polish Files:**
    - [ ] Add `add_code_of_conduct`, `add_security_md`, `add_citation_cff` booleans to `copier.yaml`.
    - [ ] Scaffold corresponding files conditionally.
    - [ ] Add exclusion rules.
    - [ ] Add tests for these files.
- [ ] **Add MkDocs Support:**
    - [ ] Ensure questions `use_docs`, `use_mkdocstrings`, `doc_hosting_provider` exist.
    - [ ] Ensure MkDocs files are scaffolded conditionally.
    - [ ] Ensure conditional `export-docs-reqs` script.

## ✅ Step 8: Final Review & Testing

- [ ] **Update `test_generated_project.py`:** Modify test commands to be task-runner aware (use `just` or `pdm run` based on the `task_runner` variable).
- [ ] **Review `copier.yaml`:** Review all questions, defaults, and `when` conditions.
- [ ] **Review Exclusions:** Review all exclusion rules.
- [ ] **Review Jinja Logic:** Review conditional logic within all `.jinja` template files.
- [ ] **Run Full Test Suite:** Run `test_project_structure.py` and the updated `test_generated_project.py`.

- [ ] document use of mise install in mise.toml in CONTRIBUTING.md for template project.

## 📖 Step 9: Documentation Review
- [ ] **Full documentation review:** Review all project documentation and update as necessary to reflect the v1 feature set.