import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
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
  });
});
