# Template v1 To-Do List

## Step 4: Implement simple task tracking alternative option
- [x] **Update Copier questions:** Update question that asks about creating to github project so that it supports 3 choices: "Configure task tracking for this project? TODO.md, Github Projects, none" default: TODO.md.
- [x] **Update copier scripts and tools:** make any necessary changes to support the new option for task tracking including adding a TODO.md.jinja file.

## 🚀 Step 5: Optional CI/CD & Dependency Management

- [x] **GitHub Push & Account:** Add `push_to_github` and `github_account` questions.
- [x] **Semantic Release:** Ensure `use_semantic_release` question and conditional workflow exclusions/dependency additions.
- [x] **Dependabot:**
    - [x] Add `use_dependabot` and `dependabot_automerge` questions to `copier.yaml`.
    - [x] Scaffold `.github/dependabot.yml.jinja` with conditional `automerge: true`.
    - [x] Add test: `test_with_dependabot_automerge`.
- [ ] **Scaffold Workflows:** Ensure all `.github/workflows/` files are correctly scaffolded and use conditional logic.

## 💻 Step 6: Optional Developer Experience Features

- [x] **`.env` File Generation:**
    - [x] Add `generate_env` boolean question to `copier.yaml`.
    - [x] Ensure `.env.jinja` exists and is conditionally excluded.
    - [x] Ensure `test_with_env_file` exists.

## 🏛️ Step 7: Optional Project Management & Documentation Features

- [x] **Automate ADR Creation:**
    - [x] Add `include_adr` boolean question to `copier.yaml`.
    - [x] Scaffold `scripts/new_adr.py`.
    - [x] Scaffold `docs/adr/0000-template.md`.
    - [x] Ensure conditional inclusion in `scripts`.
    - [x] Add exclusion rules.
    - [x] Add test: `test_with_adr_support`.
- [x] **Implement GitHub Project Scaffolding:**
    - [x] Add Github Project option for task tracking
    - [x] Ensure `bootstrap.py` exists and receives the argument in `_tasks`.
    - [x] Add test: `test_with_github_project`.
- [x] **Integrate `ROADMAP.md` and GitHub Project:**
    - [x] Scaffold `ROADMAP.md.jinja` with placeholder.
    - [x] Ensure `bootstrap.py` logic updates the placeholder.
    - [x] Ensure test `test_with_github_project` checks for the placeholder.
- [x] **Add Repository Polish Files:**
    - [x] Add `add_code_of_conduct`, `add_security_md`, `add_citation_cff` booleans to `copier.yaml`.
    - [x] Scaffold corresponding files conditionally.
    - [x] Add exclusion rules.
    - [x] Add tests for these files.
- [ ] **Add MkDocs Support:**
    - [x] Ensure questions `use_docs`, `use_mkdocstrings`, `doc_hosting_provider` exist.
    - [ ] Ensure MkDocs files are scaffolded conditionally.
    - [ ] Ensure conditional `export-docs-reqs` script.
- [ ] **Review Testing"**
    - [ ] Review test suite for best practices and determine whether there are any areas for improvement with the structure or content of existing tests.
    - [ ] Review test suite vs project code and determine if there are any additional tests needed

## ✅ Step 8: Final Review & Testing

- [ ] **Update `test_generated_project.py`:** Modify test commands to be task-runner aware (use `just` or `pdm run` based on the `task_runner` variable).
- [ ] **Review `copier.yaml`:** Review all questions, defaults, and `when` conditions and make sure that they are ordered logically.
- [ ] **Review Exclusions:** Review all exclusion rules.
- [ ] **Review Jinja Logic:** Review conditional logic within all `.jinja` template files.
- [ ] **Run Full Test Suite:** Run `test_project_structure.py` and the updated `test_generated_project.py`.

- [ ] document use of mise install in mise.toml in CONTRIBUTING.md for template project.

## 📖 Step 9: Documentation Review
- [ ] **Full documentation review:** Review all project documentation and template functionality and update as necessary to reflect the v1 feature set.