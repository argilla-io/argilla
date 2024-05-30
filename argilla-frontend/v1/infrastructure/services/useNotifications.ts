import { toast } from "~/components/base/base-toast/api";

export const useNotifications = () => {
  const clear = () => {
    toast().clear();
  };

  const notify = ({
    message,
    type = "info",
    permanent,
    buttonText,
    onClick,
    onClose,
  }: {
    message: string;
    type?: "success" | "info" | "warning" | "error";
    permanent?: boolean;
    buttonText?: string;
    onClick?: () => void;
    onClose?: () => void;
  }) => {
    return setTimeout(() => {
      toast().open({
        message,
        permanent,
        numberOfChars: message.length,
        buttonText,
        onClick() {
          clear();

          if (onClick) onClick();
        },
        onClose() {
          clear();

          if (onClose) onClose();
        },
        type: type || "default",
      });
    }, 100);
  };

  return {
    notify,
    clear,
  };
};
