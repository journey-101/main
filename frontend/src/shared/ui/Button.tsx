import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

type ButtonProps = PropsWithChildren<ButtonHTMLAttributes<HTMLButtonElement>>;

export function Button({ children, ...props }: ButtonProps) {
  return (
    <button className="button" type="button" {...props}>
      {children}
    </button>
  );
}
