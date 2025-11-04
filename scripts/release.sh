#!/bin/bash
# Release script for ZETA CLI
# Usage: ./scripts/release.sh <version>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 1.0.1"
    exit 1
fi

VERSION=$1

echo "Releasing ZETA CLI version $VERSION"
echo ""

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo "Warning: You're not on main/master branch. Current branch: $CURRENT_BRANCH"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update version in setup.py
sed -i.bak "s/version=\".*\"/version=\"$VERSION\"/" setup.py
rm setup.py.bak

# Update version in zeta.py if __version__ exists
if grep -q "__version__" zeta.py; then
    sed -i.bak "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" zeta.py
    rm zeta.py.bak
fi

# Run tests
echo "Running tests..."
python -m pytest tests/ -v

# Build package
echo "Building package..."
python -m build

# Check package
echo "Checking package..."
twine check dist/*

# Create git tag
echo "Creating git tag v$VERSION..."
git add setup.py zeta.py
git commit -m "Bump version to $VERSION" || true
git tag -a "v$VERSION" -m "Release version $VERSION"

echo ""
echo "Release preparation complete!"
echo ""
echo "Next steps:"
echo "1. Review changes: git diff HEAD~1"
echo "2. Push tag: git push origin v$VERSION"
echo "3. Push commits: git push"
echo "4. Upload to PyPI: twine upload dist/*"
echo ""
echo "Or use GitHub Actions release workflow for automated release."

