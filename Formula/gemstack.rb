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
  url "https://files.pythonhosted.org/packages/34/fc/c2692b3f459ca34bd4c76fe0972e2cb514efa3505a21be3b9902b8fcc43a/gemstack-2.0.0.tar.gz"
  sha256 "861502da220c60faefcd36cb4912dcfb920f5f436f0d4e4359c3065294832587"
  license "Apache-2.0"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "gemstack", shell_output("#{bin}/gemstack --version")
  end
end
