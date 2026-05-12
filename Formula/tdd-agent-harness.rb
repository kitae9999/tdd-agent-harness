class TddAgentHarness < Formula
  desc "Strict TDD harness for coding agents with executable quality gates"
  homepage "https://github.com/kitae9999/tdd-agent-harness"
  url "https://github.com/kitae9999/tdd-agent-harness/archive/refs/tags/v0.2.0.tar.gz"
  sha256 "d24a37d4b5bb9dfb59db4c0179461d26907eb4e40a0dc9dff29ca16699bd1375"
  license "MIT"

  head "https://github.com/kitae9999/tdd-agent-harness.git", branch: "main"

  depends_on "python@3.12"

  def install
    libexec.install "AGENTS.md"
    libexec.install "TDD_HARNESS.md"
    libexec.install "SPEC.md"
    libexec.install "TODO.md"
    libexec.install "harness.json"
    libexec.install "bin"
    libexec.install "docs"
    libexec.install "evals"
    libexec.install "scripts"
    libexec.install "skills"

    (bin/"tdd-agent-harness").write <<~EOS
      #!/bin/bash
      exec "#{libexec}/bin/tdd-agent-harness" "$@"
    EOS
  end

  test do
    system bin/"tdd-agent-harness", "--help"
  end
end
