class TddAgentHarness < Formula
  desc "Strict TDD harness for coding agents with executable quality gates"
  homepage "https://github.com/kitae9999/tdd-agent-harness"
  url "https://github.com/kitae9999/tdd-agent-harness/archive/refs/tags/v0.1.1.tar.gz"
  sha256 "aba162e5bb4a682a0198aa0e16e6b715bdec6a23aaf06764c19b6e5dad3b2cd3"
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
