# Homebrew formula for Gemstack
# Version is dynamically determined from PyPI — no hardcoded versions.
#
# Usage:
#   brew tap arvarik/gemstack https://github.com/arvarik/gemstack
#   brew install gemstack
#
# This formula creates a Python virtualenv and installs gemstack via pip.

class Gemstack < Formula
  include Language::Python::Virtualenv

  desc "Opinionated AI agent orchestration framework for software engineering"
  homepage "https://github.com/arvarik/gemstack"
  url "https://pypi.org/packages/source/g/gemstack/gemstack-0.4.0.tar.gz"
  sha256 "PLACEHOLDER_SHA256"
  license "Apache-2.0"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "gemstack", shell_output("#{bin}/gemstack --version")
  end
end
