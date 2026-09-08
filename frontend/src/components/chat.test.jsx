import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChatMessage } from "./chat.jsx";

const grounded = {
  claims: [{ text: "Under Section 3(p), TK is not patentable.", source_ids: ["e1"] }],
  sources: [{
    id: "e1", title: "Patents Act 1970", section: "3(p)", status: "in_force",
    authority: "statute", as_of: "2026-09-07",
    local_excerpt: "Section 3(p): traditional knowledge is not an invention", url: "http://x",
  }],
  warnings: [], answer_mode: "live", evidence_strength: "high",
  as_of: "2026-09-07", corpus_version: "v0", jurisdiction: "india", language: "en",
};

const abstained = {
  claims: [], sources: [],
  warnings: [{ code: "out_of_corpus", message: "no supporting source" }],
  answer_mode: "live", evidence_strength: "limited",
  as_of: "2026-09-07", corpus_version: "v0", jurisdiction: "india", language: "en",
};

describe("ChatMessage", () => {
  it("renders a grounded claim with a citation chip; clicking it opens the exact passage", () => {
    render(<ChatMessage response={grounded} />);
    expect(screen.getByText(/not patentable/)).toBeInTheDocument();
    expect(screen.getByTestId("evidence-strength")).toHaveTextContent("high");
    expect(screen.getByTestId("law-as-of")).toHaveTextContent("2026-09-07");
    fireEvent.click(screen.getByTestId("cite-e1"));
    expect(screen.getByTestId("source-drawer")).toHaveTextContent("traditional knowledge is not an invention");
  });

  it("shows an abstention notice when there are no claims", () => {
    render(<ChatMessage response={abstained} />);
    expect(screen.getByTestId("abstention")).toHaveTextContent("out_of_corpus");
    expect(screen.getByTestId("evidence-strength")).toHaveTextContent("limited");
    expect(screen.getByTestId("answer-mode")).toHaveTextContent("live");
  });

  it("withholds a claim with a missing source rather than showing unsupported guidance", () => {
    render(<ChatMessage response={{ ...grounded, sources: [] }} />);
    expect(screen.getByTestId("abstention")).toHaveTextContent("missing_citation");
    expect(screen.queryByText(/Under Section 3/)).not.toBeInTheDocument();
  });

  it("exposes extractive warnings instead of implying synthesis", () => {
    render(<ChatMessage response={{ ...grounded, answer_mode: "extractive", warnings: [{ code: "degraded", message: "Source passages without synthesis." }] }} />);
    expect(screen.getByTestId("answer-mode")).toHaveTextContent("extractive");
    expect(screen.getByText("Source passages without synthesis.")).toBeInTheDocument();
  });

  it("traps drawer focus, closes with Escape, and restores citation focus", () => {
    render(<ChatMessage response={grounded} />);
    const cite = screen.getByTestId("cite-e1");
    cite.focus();
    fireEvent.click(cite);
    expect(screen.getByRole("dialog")).toHaveAttribute("aria-modal", "true");
    expect(screen.getByRole("button", { name: "close" })).toHaveFocus();
    fireEvent.keyDown(document, { key: "Tab", shiftKey: true });
    expect(screen.getByRole("link", { name: /Open official source/ })).toHaveFocus();
    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(cite).toHaveFocus();
  });

  it("preserves the complete supported answer payload for PDF export", () => {
    const onExport = vi.fn();
    render(<ChatMessage response={grounded} onExport={onExport} />);
    fireEvent.click(screen.getByRole("button", { name: "Download PDF" }));
    expect(onExport).toHaveBeenCalledWith(grounded);
  });

  it("does not export claims withheld for missing citations", () => {
    const onExport = vi.fn();
    render(<ChatMessage response={{ ...grounded, claims: [...grounded.claims, { text: "Unsupported claim", source_ids: ["missing"] }] }} onExport={onExport} />);
    fireEvent.click(screen.getByRole("button", { name: "Download PDF" }));
    expect(onExport.mock.calls[0][0].claims).toEqual(grounded.claims);
    expect(screen.queryByText("Unsupported claim")).not.toBeInTheDocument();
  });

  it("offers the human pathway only when the backend provides it", () => {
    const onEscalate = vi.fn();
    render(<ChatMessage response={{ ...abstained, warnings: [{ code: "escalate_available", message: "A facilitator can help." }] }} onEscalate={onEscalate} />);
    fireEvent.click(screen.getByRole("button", { name: /Escalate to a facilitator/ }));
    expect(onEscalate).toHaveBeenCalledOnce();
    expect(screen.queryByText("Download PDF")).not.toBeInTheDocument();
  });
});
