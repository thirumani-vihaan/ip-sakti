import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AbsWizard, ClassificationWizard } from "./wizard.jsx";

describe("wizards", () => {
  it("ABS wizard shows a sourced obligation", async () => {
    const submit = async () => ({
      status: "decided", obligation: "Prior intimation to the State Biodiversity Board",
      authority: "State Biodiversity Board", forms: ["Form I"],
      source_id: "bda_2002_s7", rule_version: "2024.1", missing: [],
    });
    render(<AbsWizard submit={submit} />);
    fireEvent.click(screen.getByTestId("abs-run"));
    const card = await screen.findByTestId("obligation");
    expect(card).toHaveTextContent("State Biodiversity Board");
    expect(card).toHaveTextContent("bda_2002_s7");
  });

  it("ABS wizard shows insufficient info when facts are missing", async () => {
    const submit = async () => ({ status: "insufficient", missing: ["applicant"], forms: [], obligation: null });
    render(<AbsWizard submit={submit} />);
    fireEvent.click(screen.getByTestId("abs-run"));
    expect(await screen.findByTestId("insufficient")).toHaveTextContent("applicant");
  });

  it("Classification wizard shows a sourced result", async () => {
    const submit = async () => ({
      status: "decided", obligation: "Nutraceutical; FSSAI regulation applies.",
      authority: "FSSAI", forms: [], source_id: "fssai_nutraceutical", rule_version: "2024.1", missing: [],
    });
    render(<ClassificationWizard submit={submit} />);
    fireEvent.click(screen.getByTestId("classify-run"));
    expect(await screen.findByTestId("obligation")).toHaveTextContent("Nutraceutical");
  });
});
