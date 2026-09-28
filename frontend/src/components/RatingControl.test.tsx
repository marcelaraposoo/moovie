import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import RatingControl from "./RatingControl";

describe("RatingControl", () => {
  it("mostra o valor atual formatado", () => {
    render(<RatingControl value={7} onChange={vi.fn()} />);
    expect(screen.getByText("7.0/10")).toBeInTheDocument();
  });

  it("chama onChange com o novo valor ao mover o slider", () => {
    const onChange = vi.fn();
    render(<RatingControl value={5} onChange={onChange} />);

    const slider = screen.getByLabelText("Escolha uma nota de 0 a 10");
    fireEvent.change(slider, { target: { value: "8.5" } });

    expect(onChange).toHaveBeenCalledWith(8.5);
  });

  it("o slider aceita valores de 0 a 10", () => {
    render(<RatingControl value={5} onChange={vi.fn()} />);
    const slider = screen.getByLabelText("Escolha uma nota de 0 a 10") as HTMLInputElement;
    expect(slider.min).toBe("0");
    expect(slider.max).toBe("10");
  });
});
