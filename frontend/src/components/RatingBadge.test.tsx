import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RatingBadge from "./RatingBadge";

describe("RatingBadge", () => {
  it("mostra a nota com uma casa decimal", () => {
    render(<RatingBadge value={8.456} />);
    expect(screen.getByText("8.5")).toBeInTheDocument();
  });

  it("mostra 0.0 para nota zero", () => {
    render(<RatingBadge value={0} />);
    expect(screen.getByText("0.0")).toBeInTheDocument();
  });

  it("tem um aria-label acessível com a nota completa", () => {
    render(<RatingBadge value={7.2} />);
    expect(screen.getByLabelText("Nota 7.2 de 10")).toBeInTheDocument();
  });

  it("aplica a classe de tamanho grande quando size='lg'", () => {
    render(<RatingBadge value={9} size="lg" />);
    expect(screen.getByText("9.0")).toHaveClass("rating-badge-lg");
  });
});
