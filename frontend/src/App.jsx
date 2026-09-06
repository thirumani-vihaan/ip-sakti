import Chat from "./pages/Chat.jsx";
import { CompareTool } from "./components/compare.jsx";
import { AbsWizard, ClassificationWizard } from "./components/wizard.jsx";

export default function App() {
  return (
    <div className="app">
      <header className="header">
        <h1>IP-SAKTI Sahayak</h1>
      </header>
      <div className="disclaimer">Informational guidance, not legal advice. Consult a qualified professional.</div>
      <Chat />
      <section className="tools">
        <AbsWizard />
        <ClassificationWizard />
        <CompareTool />
      </section>
    </div>
  );
}
