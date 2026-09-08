import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SourcesPanel } from "./sources.jsx";
import { UploadPanel } from "./upload.jsx";
import { EscalateModal } from "./escalate.jsx";
import Chat from "../pages/Chat.jsx";
import App from "../App.jsx";
import { getSources, postAnalyze, postEscalate } from "../api/client.js";

vi.mock("../api/client.js", () => ({
  getSources: vi.fn(), postAnalyze: vi.fn(), postEscalate: vi.fn(),
  postChat: vi.fn(), postAbsCheck: vi.fn(), postClassify: vi.fn(),
  postCompare: vi.fn(), postRoadmap: vi.fn(), exportPdf: vi.fn(),
}));

const answer = {
  claims: [{ text: "A fixture passage about traditional knowledge.", source_ids: ["e1"] }],
  sources: [{ id: "e1", title: "Fixture source", status: "in_force", as_of: "2025-01-01", local_excerpt: "A fixture passage.", authority: "statute" }],
  warnings: [], evidence_strength: "high", answer_mode: "extractive",
  as_of: "2025-01-01", corpus_version: "test", jurisdiction: "india", language: "en",
};
const catalogue = {
  count: 2, corpus_version: "test",
  sources: [
    { id: "patents", title: "Patents fixture", authority_level: "statute", version: "test", effective_date: "2025-01-01", status: "in_force", jurisdiction: "india" },
    { id: "international", title: "International fixture", authority_level: "guidance", version: "test", effective_date: null, status: "not_yet_in_force", jurisdiction: "international" },
  ],
};
beforeEach(() => { vi.clearAllMocks(); localStorage.clear(); });

describe("sources ledger", () => {
  it("renders the existing catalogue response, filters documents, and resets empty results", async () => {
    getSources.mockResolvedValue(catalogue);
    render(<SourcesPanel />);
    await screen.findByText("Patents fixture");
    expect(screen.getByText("not yet in force")).toBeInTheDocument();
    fireEvent.change(screen.getByRole("textbox", { name: "Search corpus sources" }), { target: { value: "unmatched" } });
    expect(screen.getByText("No matching sources.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Reset filters" }));
    expect(screen.getByText("Patents fixture")).toBeInTheDocument();
    fireEvent.change(screen.getByRole("combobox", { name: "Filter sources by jurisdiction" }), { target: { value: "international" } });
    expect(screen.queryByText("Patents fixture")).not.toBeInTheDocument();
    expect(screen.getByText("International fixture")).toBeInTheDocument();
  });

  it("displays an honest unavailable state and retries without substituting documents", async () => {
    getSources.mockRejectedValueOnce(new Error("Request failed (404)")).mockResolvedValueOnce(catalogue);
    render(<SourcesPanel />);
    expect(await screen.findByRole("alert")).toHaveTextContent("We won’t substitute unverified documents");
    fireEvent.click(screen.getByRole("button", { name: /Try again/ }));
    await screen.findByText("Patents fixture");
    expect(getSources).toHaveBeenCalledTimes(2);
  });
});

describe("document and human pathways", () => {
  it("uploads the original File with its jurisdiction and renders the unchanged analysis shape", async () => {
    const file = new File(["traditional knowledge"], "formulation.txt", { type: "text/plain" });
    postAnalyze.mockResolvedValue({ filename: file.name, extracted_preview: "traditional knowledge", analysis: answer });
    render(<UploadPanel />);
    fireEvent.change(screen.getByLabelText("Document to analyze"), { target: { files: [file] } });
    await screen.findByTestId("chat-message");
    expect(postAnalyze).toHaveBeenCalledWith(file, "india");
    expect(screen.getByText("formulation.txt")).toBeInTheDocument();
  });

  it("rejects an oversized upload before making a request", () => {
    const file = new File(["text"], "oversize.txt", { type: "text/plain" });
    Object.defineProperty(file, "size", { value: 6 * 1024 * 1024 });
    render(<UploadPanel />);
    fireEvent.change(screen.getByLabelText("Document to analyze"), { target: { files: [file] } });
    expect(screen.getByRole("alert")).toHaveTextContent("5 MB");
    expect(postAnalyze).not.toHaveBeenCalled();
  });

  it("preserves referral payload and displays the returned reference", async () => {
    const onClose = vi.fn();
    postEscalate.mockResolvedValue({ reference_id: "FIXTURE-001", message: "Referral prepared.", facilitator: "Fixture facilitator", next_steps: ["Keep the reference."] });
    render(<EscalateModal query="A question" onClose={onClose} />);
    expect(screen.getByRole("dialog")).toHaveAttribute("aria-modal", "true");
    fireEvent.click(screen.getByRole("button", { name: "Prepare referral" }));
    await screen.findByText("FIXTURE-001");
    expect(postEscalate).toHaveBeenCalledWith({ query: "A question", contact: undefined });
    fireEvent.click(screen.getByRole("button", { name: "Done" }));
    expect(onClose).toHaveBeenCalledOnce();
  });

  it("does not fabricate a referral when its endpoint fails", async () => {
    postEscalate.mockRejectedValue(new Error("Request failed (404)"));
    render(<EscalateModal query="A question" onClose={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: "Prepare referral" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("404");
    expect(screen.queryByText("Your reference id:")).not.toBeInTheDocument();
  });
});

describe("accessible research desk", () => {
  it("supports keyboard tabs and identifies the selected panel", () => {
    render(<App />);
    const assistant = screen.getByRole("tab", { name: "Assistant" });
    assistant.focus();
    fireEvent.keyDown(assistant, { key: "ArrowRight" });
    const classify = screen.getByRole("tab", { name: "Classify" });
    expect(classify).toHaveAttribute("aria-selected", "true");
    expect(classify).toHaveFocus();
    expect(screen.getByRole("tabpanel")).toHaveAttribute("aria-labelledby", classify.id);
    fireEvent.keyDown(classify, { key: "Home" });
    expect(assistant).toHaveAttribute("aria-selected", "true");
  });

  it("preserves language and sensitive flags and never persists a sensitive answer", async () => {
    const api = vi.fn().mockResolvedValue(answer);
    render(<Chat api={api} />);
    fireEvent.change(screen.getByTestId("lang-select"), { target: { value: "te" } });
    fireEvent.click(screen.getByTestId("sensitive-toggle"));
    fireEvent.change(screen.getByLabelText("Your Ayurveda IP or regulatory question"), { target: { value: "My formulation" } });
    fireEvent.click(screen.getByRole("button", { name: "Ask" }));
    await screen.findByTestId("chat-message");
    expect(api).toHaveBeenCalledWith("My formulation", { jurisdiction: "india", language: "te", sensitive: true });
    await waitFor(() => expect(JSON.parse(localStorage.getItem("ipsakti_history_v1"))).toEqual([]));
  });

  it("keeps a failed question editable for retry", async () => {
    const api = vi.fn().mockRejectedValue(new Error("Offline server unavailable"));
    render(<Chat api={api} />);
    const input = screen.getByLabelText("Your Ayurveda IP or regulatory question");
    fireEvent.change(input, { target: { value: "My formulation" } });
    fireEvent.click(screen.getByRole("button", { name: "Ask" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Offline server unavailable");
    expect(input).toHaveValue("My formulation");
    expect(screen.getByRole("button", { name: "Ask" })).toBeEnabled();
  });
});
