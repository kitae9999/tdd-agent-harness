class TddAgentHarness < Formula
  desc "Strict TDD harness for coding agents with executable quality gates"
  homepage "https://github.com/kitae9999/tdd-agent-harness"
  url "https://github.com/kitae9999/tdd-agent-harness/archive/refs/tags/v0.1.2.tar.gz"
  sha256 "1cbb9744e0baf93919e4a6e17c89f0b1a7926b643f0c40ab589654401a95d1a7"
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
