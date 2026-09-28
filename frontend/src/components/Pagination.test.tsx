import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import Pagination from "./Pagination";

describe("Pagination", () => {
  it("não renderiza nada quando há 1 página ou menos", () => {
    const { container } = render(<Pagination page={1} pages={1} onChange={vi.fn()} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("mostra a página atual e o total de páginas", () => {
    render(<Pagination page={2} pages={5} onChange={vi.fn()} />);
    expect(screen.getByText("Página 2 de 5")).toBeInTheDocument();
  });

  it("desabilita 'Anterior' na primeira página e 'Próxima' na última", () => {
    const { rerender } = render(<Pagination page={1} pages={3} onChange={vi.fn()} />);
    expect(screen.getByText("← Anterior")).toBeDisabled();
    expect(screen.getByText("Próxima →")).not.toBeDisabled();

    rerender(<Pagination page={3} pages={3} onChange={vi.fn()} />);
    expect(screen.getByText("← Anterior")).not.toBeDisabled();
    expect(screen.getByText("Próxima →")).toBeDisabled();
  });

  it("chama onChange com a página seguinte/anterior ao clicar", () => {
    const onChange = vi.fn();
    render(<Pagination page={2} pages={5} onChange={onChange} />);

    fireEvent.click(screen.getByText("Próxima →"));
    expect(onChange).toHaveBeenCalledWith(3);

    fireEvent.click(screen.getByText("← Anterior"));
    expect(onChange).toHaveBeenCalledWith(1);
  });
});
