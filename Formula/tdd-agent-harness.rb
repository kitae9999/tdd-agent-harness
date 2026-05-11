class TddAgentHarness < Formula
  desc "Strict TDD harness for coding agents with executable quality gates"
  homepage "https://github.com/kitae9999/tdd-agent-harness"
  url "https://github.com/kitae9999/tdd-agent-harness/archive/refs/tags/v0.1.3.tar.gz"
  sha256 "204a790b787190a90b210e2b000cf9e714547cd18d7a6eca5fe954de54a5c879"
  license "MIT"

  head "https://github.com/kitae9999/tdd-agent-harness.git", branch: "main"

  depends_on "python@3.12"

  def install
    libexec.install "AGENTS.md"
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
