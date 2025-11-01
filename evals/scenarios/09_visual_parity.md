# Eval Scenario 09: Visual Parity Testing for Odoo Customizations

**Skill**: odoo-module-dev
**Complexity**: High
**Estimated Time**: 8-12 minutes

---

## Objective

Implement visual regression testing for Odoo UI customizations:
- Screenshot capture of Odoo views before/after changes
- Pixel-level comparison using SSIM (Structural Similarity Index)
- Automated visual parity validation in CI/CD
- Threshold-based pass/fail criteria (SSIM ≥0.95)

---

## Scenario

**Task**: "Create visual regression testing infrastructure for an Odoo module with custom views. Detect unintended UI changes during development.

**Module**: `expense_approval`
**Views to Test**:
- Form view: `expense_approval_form`
- List view: `expense_approval_tree`
- Kanban view: `expense_approval_kanban`

**Requirements**:
1. Capture screenshots using Playwright
2. Compare screenshots with SSIM algorithm
3. Store baseline screenshots for reference
4. Fail tests if SSIM < 0.95 (5% difference threshold)
5. Generate visual diff reports for failures

Expected deliverables:
1. Screenshot capture script (scripts/capture_screenshots.js)
2. SSIM comparison script (scripts/compare_screenshots.py)
3. Baseline screenshot storage strategy
4. CI/CD integration for automated testing"

---

## Pass Criteria

### Screenshot Capture Script (`scripts/capture_screenshots.js`)
```javascript
/**
 * capture_screenshots.js - Playwright screenshot capture for Odoo views
 * Usage: node scripts/capture_screenshots.js --url http://localhost:8069 --output ./screenshots
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function captureOdooScreenshots(config) {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 },
        locale: 'en-US'
    });
    const page = await context.newPage();

    console.log('🎬 Starting Odoo screenshot capture...');

    try {
        // Login to Odoo
        console.log('Logging in...');
        await page.goto(`${config.url}/web/login`);
        await page.fill('input[name="login"]', config.username || 'admin');
        await page.fill('input[name="password"]', config.password || 'admin');
        await page.click('button[type="submit"]');
        await page.waitForURL('**/web', { timeout: 10000 });

        // Navigate to expense_approval module
        console.log('Navigating to expense_approval...');
        await page.goto(`${config.url}/web#action=expense_approval.action_expense_approval`);
        await page.waitForSelector('.o_content', { timeout: 10000 });

        // Test scenarios
        const scenarios = [
            {
                name: 'expense_approval_list',
                selector: '.o_list_view',
                description: 'Expense Approval List View'
            },
            {
                name: 'expense_approval_form',
                selector: '.o_form_view',
                description: 'Expense Approval Form View',
                setup: async () => {
                    // Click "Create" button to open form
                    await page.click('.o_list_button_add');
                    await page.waitForSelector('.o_form_view', { timeout: 5000 });
                }
            },
            {
                name: 'expense_approval_kanban',
                selector: '.o_kanban_view',
                description: 'Expense Approval Kanban View',
                setup: async () => {
                    // Switch to kanban view
                    await page.click('.o_cp_switch_kanban');
                    await page.waitForSelector('.o_kanban_view', { timeout: 5000 });
                }
            }
        ];

        // Capture screenshots for each scenario
        for (const scenario of scenarios) {
            console.log(`\nCapturing: ${scenario.description}`);

            // Run setup if provided
            if (scenario.setup) {
                await scenario.setup();
            }

            // Wait for content to load
            await page.waitForSelector(scenario.selector, { timeout: 10000 });

            // Wait for any animations to complete
            await page.waitForTimeout(1000);

            // Capture screenshot
            const screenshotPath = path.join(
                config.outputDir,
                `${scenario.name}.png`
            );

            await page.screenshot({
                path: screenshotPath,
                fullPage: false,  // Capture viewport only
                clip: await page.locator(scenario.selector).boundingBox()
            });

            console.log(`✅ Saved: ${screenshotPath}`);

            // Navigate back to list view for next test
            if (scenario.name !== 'expense_approval_list') {
                await page.goto(`${config.url}/web#action=expense_approval.action_expense_approval`);
                await page.waitForSelector('.o_content', { timeout: 5000 });
            }
        }

        console.log('\n✅ Screenshot capture complete!');

    } catch (error) {
        console.error('❌ Error during screenshot capture:', error);
        throw error;
    } finally {
        await browser.close();
    }
}

// Parse command-line arguments
const args = process.argv.slice(2);
const config = {
    url: args.find(a => a.startsWith('--url='))?.split('=')[1] || 'http://localhost:8069',
    outputDir: args.find(a => a.startsWith('--output='))?.split('=')[1] || './screenshots',
    username: args.find(a => a.startsWith('--user='))?.split('=')[1] || 'admin',
    password: args.find(a => a.startsWith('--pass='))?.split('=')[1] || 'admin'
};

// Ensure output directory exists
if (!fs.existsSync(config.outputDir)) {
    fs.mkdirSync(config.outputDir, { recursive: true });
}

// Run capture
captureOdooScreenshots(config).catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
```

### SSIM Comparison Script (`scripts/compare_screenshots.py`)
```python
#!/usr/bin/env python3
"""
compare_screenshots.py - SSIM-based visual regression testing
Usage: python scripts/compare_screenshots.py --baseline ./baseline --current ./screenshots
"""
import argparse
import sys
from pathlib import Path
from typing import Tuple

from PIL import Image
import numpy as np
from skimage.metrics import structural_similarity as ssim


def load_image(path: Path) -> np.ndarray:
    """Load image and convert to grayscale numpy array"""
    image = Image.open(path).convert('L')  # Convert to grayscale
    return np.array(image)


def compare_images(baseline_path: Path, current_path: Path) -> Tuple[float, np.ndarray]:
    """
    Compare two images using SSIM (Structural Similarity Index)

    Args:
        baseline_path: Path to baseline screenshot
        current_path: Path to current screenshot

    Returns:
        (ssim_score, diff_image): SSIM score (0-1) and difference visualization
    """
    baseline = load_image(baseline_path)
    current = load_image(current_path)

    # Ensure images are same size
    if baseline.shape != current.shape:
        print(f"⚠️  Warning: Image size mismatch - {baseline.shape} vs {current.shape}")
        # Resize current to match baseline
        current_pil = Image.fromarray(current).resize((baseline.shape[1], baseline.shape[0]))
        current = np.array(current_pil)

    # Calculate SSIM
    ssim_score, diff_image = ssim(baseline, current, full=True)

    # Convert diff to image (0-255 range)
    diff_image = (diff_image * 255).astype(np.uint8)

    return ssim_score, diff_image


def main():
    parser = argparse.ArgumentParser(description='Visual regression testing with SSIM')
    parser.add_argument('--baseline', required=True, help='Baseline screenshots directory')
    parser.add_argument('--current', required=True, help='Current screenshots directory')
    parser.add_argument('--threshold', type=float, default=0.95, help='SSIM threshold (default: 0.95)')
    parser.add_argument('--output', default='./visual_diff', help='Output directory for diff images')
    args = parser.parse_args()

    baseline_dir = Path(args.baseline)
    current_dir = Path(args.current)
    output_dir = Path(args.output)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print('🔍 Visual Parity Testing')
    print('========================')
    print(f'Baseline: {baseline_dir}')
    print(f'Current:  {current_dir}')
    print(f'Threshold: SSIM ≥ {args.threshold}')
    print()

    # Find all baseline screenshots
    baseline_screenshots = sorted(baseline_dir.glob('*.png'))
    if not baseline_screenshots:
        print('❌ No baseline screenshots found')
        sys.exit(1)

    results = []
    failed = []

    for baseline_path in baseline_screenshots:
        current_path = current_dir / baseline_path.name

        if not current_path.exists():
            print(f'⚠️  SKIP: {baseline_path.name} (no current screenshot)')
            continue

        # Compare screenshots
        ssim_score, diff_image = compare_images(baseline_path, current_path)

        # Save diff image
        diff_path = output_dir / f'diff_{baseline_path.name}'
        Image.fromarray(diff_image).save(diff_path)

        # Check against threshold
        passed = ssim_score >= args.threshold
        status = '✅ PASS' if passed else '❌ FAIL'

        print(f'{status}: {baseline_path.name} - SSIM: {ssim_score:.4f}')

        results.append({
            'name': baseline_path.name,
            'ssim': ssim_score,
            'passed': passed,
            'diff_path': diff_path
        })

        if not passed:
            failed.append(baseline_path.name)

    # Summary
    print()
    print('========================')
    print(f'Total: {len(results)} | Passed: {len([r for r in results if r["passed"]])} | Failed: {len(failed)}')

    if failed:
        print()
        print('Failed Screenshots:')
        for name in failed:
            result = next(r for r in results if r['name'] == name)
            print(f'  - {name}: SSIM {result["ssim"]:.4f} (threshold: {args.threshold})')
            print(f'    Diff: {result["diff_path"]}')
        sys.exit(1)
    else:
        print()
        print('✅ All visual parity tests passed!')
        sys.exit(0)


if __name__ == '__main__':
    main()
```

### Baseline Storage Strategy

**Directory Structure**:
```
tests/visual_baselines/
├── expense_approval_list.png       # Baseline for list view
├── expense_approval_form.png       # Baseline for form view
├── expense_approval_kanban.png     # Baseline for kanban view
└── metadata.json                   # Version info, capture date
```

**metadata.json**:
```json
{
    "odoo_version": "16.0",
    "module_version": "16.0.1.0.0",
    "capture_date": "2025-11-01T10:30:00Z",
    "viewport": {
        "width": 1920,
        "height": 1080
    },
    "screenshots": [
        {
            "name": "expense_approval_list.png",
            "view_type": "list",
            "hash": "abc123def456"
        },
        {
            "name": "expense_approval_form.png",
            "view_type": "form",
            "hash": "def456ghi789"
        },
        {
            "name": "expense_approval_kanban.png",
            "view_type": "kanban",
            "hash": "ghi789jkl012"
        }
    ]
}
```

### CI/CD Integration (`.github/workflows/visual_parity.yml`)
```yaml
name: Visual Parity Testing

on:
  pull_request:
    paths:
      - 'custom_addons/expense_approval/**/*.xml'  # View changes
      - 'custom_addons/expense_approval/**/*.css'  # Style changes
      - 'custom_addons/expense_approval/**/*.scss'

jobs:
  visual_regression:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          npm install playwright
          npx playwright install --with-deps chromium
          pip install Pillow numpy scikit-image

      - name: Start Odoo (Docker)
        run: |
          docker-compose up -d
          sleep 30  # Wait for Odoo to start

      - name: Capture current screenshots
        run: |
          node scripts/capture_screenshots.js \
            --url http://localhost:8069 \
            --output ./screenshots

      - name: Compare with baselines
        run: |
          python scripts/compare_screenshots.py \
            --baseline ./tests/visual_baselines \
            --current ./screenshots \
            --threshold 0.95 \
            --output ./visual_diff

      - name: Upload diff images on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: visual-diff-images
          path: ./visual_diff/*.png

      - name: Stop Odoo
        if: always()
        run: docker-compose down
```

### Validation Checklist
- ✅ Playwright captures screenshots of all views
- ✅ SSIM comparison detects ≥5% visual differences
- ✅ Baseline screenshots stored in version control
- ✅ CI/CD fails on visual regression (SSIM < 0.95)
- ✅ Diff images generated for failed comparisons
- ✅ Metadata tracks Odoo version and viewport

---

## Execution

### Automated Check
```bash
#!/bin/bash
set -e

echo "🧪 Eval Scenario 09: Visual Parity Testing"
echo "=========================================="

# Test 1: Screenshot capture script validation
echo "Test 1: Screenshot Capture Script"
if [ -f "scripts/capture_screenshots.js" ]; then
    if grep -q "playwright" scripts/capture_screenshots.js && \
       grep -q "screenshot" scripts/capture_screenshots.js && \
       grep -q "o_list_view\|o_form_view\|o_kanban_view" scripts/capture_screenshots.js; then
        echo "✅ Playwright screenshot script valid"
    else
        echo "❌ Screenshot script missing Playwright or view selectors"
        exit 1
    fi
else
    echo "❌ scripts/capture_screenshots.js not found"
    exit 1
fi

# Test 2: SSIM comparison script validation
echo ""
echo "Test 2: SSIM Comparison Script"
if [ -f "scripts/compare_screenshots.py" ]; then
    if grep -q "from skimage.metrics import structural_similarity" scripts/compare_screenshots.py && \
       grep -q "ssim_score.*threshold" scripts/compare_screenshots.py; then
        echo "✅ SSIM comparison script valid"
    else
        echo "❌ Comparison script missing SSIM implementation"
        exit 1
    fi
else
    echo "❌ scripts/compare_screenshots.py not found"
    exit 1
fi

# Test 3: Baseline storage structure
echo ""
echo "Test 3: Baseline Storage Structure"
if [ -d "tests/visual_baselines" ]; then
    echo "✅ Baseline directory exists"

    # Check for metadata.json
    if [ -f "tests/visual_baselines/metadata.json" ]; then
        echo "✅ Metadata file present"
    else
        echo "⚠️  Warning: metadata.json not found"
    fi
else
    echo "⚠️  tests/visual_baselines directory not found (will be created)"
fi

# Test 4: CI/CD integration
echo ""
echo "Test 4: CI/CD Workflow Integration"
if [ -f ".github/workflows/visual_parity.yml" ]; then
    if grep -q "playwright\|compare_screenshots" .github/workflows/visual_parity.yml; then
        echo "✅ Visual parity workflow configured"
    else
        echo "⚠️  Warning: Workflow missing visual testing steps"
    fi
else
    echo "⚠️  .github/workflows/visual_parity.yml not found"
fi

# Test 5: Dependencies check
echo ""
echo "Test 5: Dependencies Validation"
MISSING_DEPS=0

if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not installed"
    MISSING_DEPS=$((MISSING_DEPS + 1))
fi

if ! python3 -c "import PIL" 2>/dev/null; then
    echo "⚠️  Pillow not installed (pip install Pillow)"
    MISSING_DEPS=$((MISSING_DEPS + 1))
fi

if ! python3 -c "import skimage" 2>/dev/null; then
    echo "⚠️  scikit-image not installed (pip install scikit-image)"
    MISSING_DEPS=$((MISSING_DEPS + 1))
fi

if [ $MISSING_DEPS -eq 0 ]; then
    echo "✅ All dependencies available"
else
    echo "⚠️  $MISSING_DEPS dependencies missing (install for full validation)"
fi

echo ""
echo "=========================================="
echo "✅ Eval Scenario 09: PASS - Visual Parity Infrastructure Complete"
echo "=========================================="
```

---

## Expected Output

```
🧪 Eval Scenario 09: Visual Parity Testing
==========================================

🎬 Starting Odoo screenshot capture...
Logging in...
Navigating to expense_approval...

Capturing: Expense Approval List View
✅ Saved: ./screenshots/expense_approval_list.png

Capturing: Expense Approval Form View
✅ Saved: ./screenshots/expense_approval_form.png

Capturing: Expense Approval Kanban View
✅ Saved: ./screenshots/expense_approval_kanban.png

✅ Screenshot capture complete!

---

🔍 Visual Parity Testing
========================
Baseline: ./tests/visual_baselines
Current:  ./screenshots
Threshold: SSIM ≥ 0.95

✅ PASS: expense_approval_list.png - SSIM: 0.9876
✅ PASS: expense_approval_form.png - SSIM: 0.9921
✅ PASS: expense_approval_kanban.png - SSIM: 0.9854

========================
Total: 3 | Passed: 3 | Failed: 0

✅ All visual parity tests passed!
```

---

## Failure Modes

### Common Failures
1. **No Baselines**: Missing baseline screenshots for comparison
2. **SSIM < Threshold**: Visual changes detected (intentional or bugs)
3. **Screenshot Timeout**: Odoo views not loading in time
4. **Size Mismatch**: Baseline and current screenshots different dimensions
5. **Missing Dependencies**: Playwright, Pillow, or scikit-image not installed

### Remediation
- Create initial baselines: `node scripts/capture_screenshots.js --output ./tests/visual_baselines`
- Update baselines after intentional UI changes
- Increase timeouts for slow-loading views
- Use consistent viewport size (1920x1080)
- Install dependencies: `npm install playwright && pip install Pillow scikit-image`

---

## OCA Best Practices

**Visual Testing Guidelines**:
1. ✅ Use SSIM for perceptual similarity (better than pixel-diff)
2. ✅ Set threshold at 0.95 (5% tolerance for anti-aliasing)
3. ✅ Store baselines in version control (tests/visual_baselines/)
4. ✅ Capture consistent viewport size (1920x1080)
5. ✅ Wait for animations to complete before screenshot
6. ❌ Don't compare dynamic content (timestamps, record IDs)
7. ❌ Don't use pixel-by-pixel comparison (too brittle)

**When to Update Baselines**:
- Intentional UI design changes
- Odoo version upgrades (visual changes expected)
- New features adding UI elements
- CSS/SCSS style updates

**Threshold Guidelines**:
- **0.99-1.00**: Pixel-perfect match (rare in practice)
- **0.95-0.99**: Acceptable match (anti-aliasing, font rendering)
- **0.90-0.95**: Minor differences (investigate)
- **< 0.90**: Major differences (likely regression)

---

## References

- [Playwright Documentation](https://playwright.dev/)
- [SSIM Algorithm](https://en.wikipedia.org/wiki/Structural_similarity)
- [scikit-image SSIM](https://scikit-image.org/docs/stable/api/skimage.metrics.html#skimage.metrics.structural_similarity)
- [Visual Regression Testing Best Practices](https://docs.percy.io/docs/best-practices)

---

**Last Reviewed**: 2025-11-01
**Maintainer**: Odoo Expertise Agent (QA2)
**Sprint**: Sprint 3 - QA Track
