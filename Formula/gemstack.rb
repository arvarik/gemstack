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

  desc "Opinionated AI agent orchestration framework for Gemini CLI and Antigravity"
  homepage "https://github.com/arvarik/gemstack"
  url "https://files.pythonhosted.org/packages/source/g/gemstack/gemstack-1.0.1.tar.gz"
  sha256 "051b8c246c659ab305e32c2d5f3ee050d7f201df9543f143aed9071d1f0b9e3e"
  license "Apache-2.0"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "gemstack", shell_output("#{bin}/gemstack --version")
  end
end
