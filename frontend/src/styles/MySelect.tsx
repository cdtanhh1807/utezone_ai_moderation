import { Listbox, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import styles from '../components/content/admin/AdminDashboard.module.css';

type Option = { value: string; label: string };

export default function MySelect({
  value,
  onChange,
  options,
  placeholder
}: {
  value: string;
  onChange: (v: string) => void;
  options: Option[];
  placeholder: string;
}) {
  const selectedLabel = options.find((o) => o.value === value)?.label ?? placeholder;

  return (
    <Listbox value={value} onChange={onChange}>
      <div className={styles.customSelectWrapper}>
        <Listbox.Button className={styles.customSelectBtn}>{selectedLabel}</Listbox.Button>
        <Transition as={Fragment} leave="transition ease-in duration-100" leaveFrom="opacity-100" leaveTo="opacity-0">
          <Listbox.Options className={styles.customSelectOptions}>
            {options.map((opt) => (
              <Listbox.Option key={opt.value} value={opt.value} as={Fragment}>
                {({ active }) => (
                  <li className={`${styles.customOption} ${active ? styles.activeOption : ''}`}>
                    {opt.label}
                  </li>
                )}
              </Listbox.Option>
            ))}
          </Listbox.Options>
        </Transition>
      </div>
    </Listbox>
  );
}