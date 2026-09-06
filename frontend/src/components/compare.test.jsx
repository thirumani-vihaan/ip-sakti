import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import Chat from "../pages/Chat.jsx";
import { CompareTool } from "./compare.jsx";

const fakeResp = {
  claims: [{ text: "ok", source_ids: ["e1"] }],
  sources: [{ id: "e1", title: "t", section: "3(p)", status: "in_force", authority: "statute", as_of: "2026-09-07", local_excerpt: "x" }],
  warnings: [], answer_mode: "live", evidence_strength: "high",
  as_of: "2026-09-07", corpus_version: "v0", jurisdiction: "india", language: "en",
};

describe("controls + compare", () => {
  it("jurisdiction, language, and sensitive toggle are passed to the API", async () => {
    const api = vi.fn(async () => fakeResp);
    render(<Chat api={api} />);
    fireEvent.click(screen.getByTestId("jur-toggle")); // india -> international
    fireEvent.click(screen.getByTestId("sensitive-toggle")); // sensitive on
    fireEvent.change(screen.getByPlaceholderText(/Ask about/), { target: { value: "test query" } });
    fireEvent.click(screen.getByText("Ask"));
    expect(api).toHaveBeenCalledWith("test query", { jurisdiction: "international", sensitive: true, language: "en" });
  });

  it("CompareTool renders two answers side by side", async () => {
    const submit = async () => ({ a: fakeResp, b: fakeResp });
    render(<CompareTool submit={submit} />);
    fireEvent.click(screen.getByTestId("compare-run"));
    expect(await screen.findAllByTestId("chat-message")).toHaveLength(2);
  });
});
