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
  url "https://files.pythonhosted.org/packages/source/g/gemstack/gemstack-1.0.0.tar.gz"
  sha256 "a312a9f31061e6ed0c9835c0dd41a0aaa362bb9f8955d64a102a7eb540819d07"
  license "Apache-2.0"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "gemstack", shell_output("#{bin}/gemstack --version")
  end
end
