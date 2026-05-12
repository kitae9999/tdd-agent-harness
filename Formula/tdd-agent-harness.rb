class TddAgentHarness < Formula
  desc "Strict TDD harness for coding agents with executable quality gates"
  homepage "https://github.com/kitae9999/tdd-agent-harness"
  url "https://github.com/kitae9999/tdd-agent-harness/archive/refs/tags/v0.2.1.tar.gz"
  sha256 "26c69dd00f74e8b0b9615a14c43a5b64013903205f576a82fd7dc000fb00e004"
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
