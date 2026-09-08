import { useEffect, useRef } from "react";

const paths = {
  spark: <><path d="m12 3 2.6 6.4L21 12l-6.4 2.6L12 21l-2.6-6.4L3 12l6.4-2.6L12 3Z" /><path d="m20 2 .6 1.4L22 4l-1.4.6L20 6l-.6-1.4L18 4l1.4-.6L20 2Z" /></>,
  leaf: <><path d="M20 4C8 2 2 9 6 16s15 1 14-12Z" /><path d="M4 21 16 9M9 16l-1-5m5 1 5 1" /></>,
  shield: <><path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z" /><path d="m8 12 3 3 5-6" /></>,
  book: <><path d="M12 6v15M12 6C8 3 4 3 2 4v15c3-1 6-1 10 2 4-3 7-3 10-2V4c-3-1-6-1-10 2Z" /></>,
  grid: <><rect x="3" y="3" width="7" height="7" rx="2" /><rect x="14" y="3" width="7" height="7" rx="2" /><rect x="3" y="14" width="7" height="7" rx="2" /><rect x="14" y="14" width="7" height="7" rx="2" /></>,
  compare: <><path d="M12 3v18M8 5H4v14h4M16 5h4v14h-4M7 9l3 3-3 3m10-6-3 3 3 3" /></>,
  route: <><circle cx="6" cy="5" r="2" /><circle cx="18" cy="19" r="2" /><path d="M8 5h8a4 4 0 0 1 0 8H8a3 3 0 0 0 0 6h8" /></>,
  upload: <><path d="M12 16V3m-5 5 5-5 5 5M4 15v5a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-5" /></>,
  arrow: <><path d="M4 12h16m-6-6 6 6-6 6" /></>,
  external: <><path d="M14 3h7v7m0-7L10 14M10 3H4a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h16a1 1 0 0 0 1-1v-6" /></>,
  globe: <><circle cx="12" cy="12" r="9" /><ellipse cx="12" cy="12" rx="4" ry="9" /><path d="M3 12h18" /></>,
  lock: <><rect x="5" y="10" width="14" height="11" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  close: <path d="m6 6 12 12M6 18 18 6" />,
  download: <><path d="M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4" /></>,
  search: <><circle cx="10" cy="10" r="7" /><path d="m15 15 6 6" /></>,
  info: <><circle cx="12" cy="12" r="9" /><path d="M12 11v6m0-10v1" /></>,
};

export function Icon({ name, className = "", ...props }) {
  return <svg className={`icon ${className}`} width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{paths[name] || paths.book}</svg>;
}

export function BotanicalFolio() {
  return (
    <div className="botanical-folio" aria-hidden="true">
      <div className="folio-top"><span>THE KNOWLEDGE FOLIO</span><span>№ 01</span></div>
      <svg className="botanical" viewBox="0 0 420 320" fill="none">
        <circle cx="219" cy="160" r="124" stroke="currentColor" opacity=".16" />
        <circle cx="219" cy="160" r="103" stroke="currentColor" opacity=".1" strokeDasharray="2 8" />
        <path d="M216 290C231 229 204 193 220 133C229 101 244 66 258 33" stroke="currentColor" strokeWidth="2" />
        <g stroke="currentColor" strokeWidth="1.3">
          <path d="M219 234C157 229 127 194 131 164C179 156 217 187 219 234ZM219 234l-76-60m21 19-23 2m42 13-6-22m25 36-27 1" />
          <path d="M216 202C267 205 305 175 310 142C264 135 226 164 216 202Zm0 0 81-51m-23 15 23 2m-41 10 8-22m-25 33 26 2" />
          <path d="M219 157C174 160 145 124 149 91C189 91 219 119 219 157Zm0 0-59-55m20 19-20-1m36 17-4-20" />
          <path d="M230 111C270 122 303 100 313 69C274 58 242 79 230 111Zm0 0 70-34m-44 22 6-17m9 10 19 4" />
          <path d="M247 65C218 49 224 23 244 11C264 29 265 46 247 65Zm0 0-3-42" />
          <path d="M212 275c-17 2-31 9-36 19m45-22c18 1 30 9 33 17" opacity=".6" />
        </g>
        <path className="draw-thread" d="M139 175H68q-12 0-12 12v32M294 86h57q12 0 12 12v20" stroke="currentColor" strokeWidth="1" />
        <circle cx="139" cy="175" r="4" fill="currentColor" />
        <circle cx="294" cy="86" r="4" fill="currentColor" />
      </svg>
      <div className="folio-label folio-label-one"><span>01</span>Rooted in tradition</div>
      <div className="folio-label folio-label-two"><span>02</span>Linked to evidence</div>
      <div className="folio-bottom"><span>Ancient knowledge.<br /><em>A traceable future.</em></span><Icon name="spark" /></div>
    </div>
  );
}

export function useDialog(onClose, active = true) {
  const ref = useRef(null);
  const close = useRef(onClose);
  close.current = onClose;
  useEffect(() => {
    if (!active) return undefined;
    const previous = document.activeElement;
    const oldOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const focusable = () => [...(ref.current?.querySelectorAll('button:not(:disabled), a[href], input, select, textarea, [tabindex="0"]') || [])];
    (focusable()[0] || ref.current)?.focus();
    const keydown = (e) => {
      if (e.key === "Escape") close.current();
      if (e.key === "Tab") {
        const nodes = focusable();
        if (!nodes.length) { e.preventDefault(); return; }
        const first = nodes[0], last = nodes[nodes.length - 1];
        if (e.shiftKey && (document.activeElement === first || !ref.current?.contains(document.activeElement))) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && (document.activeElement === last || !ref.current?.contains(document.activeElement))) { e.preventDefault(); first.focus(); }
      }
    };
    document.addEventListener("keydown", keydown);
    return () => {
      document.body.style.overflow = oldOverflow;
      document.removeEventListener("keydown", keydown);
      previous?.focus();
    };
  }, [active]);
  return ref;
}
