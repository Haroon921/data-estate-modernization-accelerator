# Contributing

Thank you for helping improve the Data Estate Modernization Accelerator.

## Good contributions

- Add assessment signals or routing rules backed by documented product behavior.
- Improve migration and rollback guidance with reproducible steps.
- Add validation checks that produce auditable evidence.
- Correct obsolete SKU, API, feature-support, or pricing references.
- Improve examples without including customer data, credentials, or tenant-specific identifiers.

Open an issue before making a large architectural change so that the approach can be agreed before implementation.

## Development setup

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

Activate the environment using the command for your operating system, then run the smoke checks:

```bash
python -m compileall assess business-case decide modernize validate
python decide/router.py assess/sample_inventory.csv
```

## Pull request workflow

1. Create a focused branch from the default branch.
2. Make one logical change and update directly related documentation.
3. Do not commit secrets, connection strings, customer data, or generated assessment output.
4. Run the relevant checks locally.
5. Complete the pull request template, including validation evidence and documentation impact.
6. Request review from an appropriate data, platform, or security specialist.

## Quality expectations

- Keep routing decisions deterministic and include a clear rationale and watch-out.
- Treat prices, sizing ratios, and support claims as time-sensitive.
- Prefer secure defaults and document permissions required by every operation.
- Preserve compatibility with Python 3.10 or later.
- Use sample or synthetic data only.
- Keep changes narrowly scoped and easy to review.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
